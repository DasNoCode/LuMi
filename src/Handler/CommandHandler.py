from __future__ import annotations
import traceback
import re
import os
import importlib.util
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING
from Helpers import JsonObject, get_rank

if TYPE_CHECKING:
    from Libs import SuperClient, Message, BaseCommand
    from Models import User


class CommandHandler:
    FLAG_PATTERN = re.compile(r"(\w+):([\w\-/]+|'[^']+'|\"[^\"]+\")")

    def __init__(self, client: SuperClient) -> None:
        self._client: SuperClient = client
        self._commands: Dict[str, BaseCommand] = {}
        self._aliases_map: Dict[str, str] = {}

    def _parse_args(self, raw: str) -> Dict[str, Any]:
        parts = raw.split()
        if not parts:
            return {"cmd": "", "text": "", "flags": {}, "raw": raw}

        prefix = self._client.config.prefix
        first = parts[0].lower()

        if first.startswith(prefix):
            cmd_name = first[len(prefix) :]
        elif first.startswith("cmd:"):
            cmd_name = first[4:]
        else:
            cmd_name = ""

        text_content = " ".join(parts[1:]) if cmd_name else raw
        flags = {
            m.group(1): m.group(2).strip("'\"")
            for m in self.FLAG_PATTERN.finditer(text_content)
        }
        clean_text = self.FLAG_PATTERN.sub("", text_content).strip()

        return {
            "cmd": cmd_name,
            "text": clean_text,
            "flags": flags,
            "raw": raw,
        }

    def load_commands(self, folder_path: str) -> None:
        self._client.log.info("🚀 Loading commands...")
        all_files = self._client.utils.readdir_recursive(folder_path)

        for file_path in all_files:
            if not file_path.endswith(".py") or os.path.basename(file_path).startswith(
                "_"
            ):
                continue
            try:
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                CommandClass = getattr(module, "Command", None)
                if not CommandClass:
                    continue

                inst: BaseCommand = CommandClass(self._client, self)
                cmd_name = inst.config.command.lower()

                self._commands[cmd_name] = inst
                for alias in getattr(inst.config, "aliases", []):
                    self._aliases_map[alias.lower()] = cmd_name

                self._client.log.info(f"✅ Loaded: {cmd_name}")
            except Exception as e:
                self._client.log.error(f"❌ Failed to load {file_path}: {e}")

    async def handler(self, M: Message) -> None:
        raw_msg = M.message
        chat_name: str = M.chat_title if M.chat_type == "supergroup" else "private"
        if not raw_msg and not M.is_callback:
            return

        is_cmd = M.is_callback or raw_msg.startswith(self._client.config.prefix)
        msg_type: str = "CMD" if is_cmd else "MSG"
        context = JsonObject(self._parse_args(raw_msg))

        sender_db: User = self._client.db.get_user_by_user_id(M.sender.user_id)

        if sender_db.afk.get("status") and context.cmd != "afk":
            await self._handle_afk_return(M, sender_db)

        await self._check_mentioned_afk(M)

        if is_cmd:
            self._client.log.info(
                f"[{msg_type}] {self._client.config.prefix}{context.cmd} from "
                f"{M.sender.mention} in {chat_name}"
            )
        else:
            return self._client.log.info(
                f"[{msg_type}] from {M.sender.mention} in {chat_name}"
            )

        cmd_key = context.cmd.lower()
        target_name = self._aliases_map.get(cmd_key, cmd_key)
        cmd_obj = self._commands.get(target_name)

        if not cmd_obj:
            return await self._client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>Unknown Command</i>』 ❌\n"
                    f"└ Use {self._client.config.prefix}help to see all available commands"
                ),
                reply_to_message_id=M.message_id,parse_mode="HTML",
            )

        if sender_db.ban.get("status"):
            text = (
                "『<i>Access Restricted</i>』 🚫\n"
                f"├ Reason: {sender_db.ban.get('reason')}\n"
                f"├ Banned At: {self._client.utils.format_duration(sender_db.ban.get('since', None))}\n"
                "└ Contact admin if this is a mistake"
            )
            await self._client.bot.send_message(
                chat_id=M.chat_id, text=text, reply_to_message_id=M.message_id, parse_mode="HTML",
            )
            return

        cmd_info = self._client.db.get_cmd_info(cmd_obj.config.command)
        if not cmd_info.get("enabled", True):
            return await self._client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>Command Disabled</i>』 ⚠️\n"
                    f"└ {cmd_obj.config.command} is currently disabled"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )

        if not await self._validate_access(M, cmd_obj):
            return

        try:
            await cmd_obj.exec(M, context)
            if getattr(cmd_obj.config, "xp", None):
                await self._process_xp(M, sender_db, cmd_obj.config.xp)
        except Exception:
            self._client.log.error(
                f"Error in {cmd_obj.config.command}: {traceback.format_exc()}"
            )

    async def _check_mentioned_afk(self, M: Message):
        targets = []
        if M.reply_to_user:
            targets.append(M.reply_to_user)
        if M.mentions:
            targets.extend(M.mentions)

        for user in targets:
            if user.user_id == M.sender.user_id:
                continue

            data = self._client.db.get_user_by_user_id(user.user_id)
            if data.afk.get("status"):
                self._client.db.set_user_afk(
                    user_id=user.user_id, mentioned_msg_id=M.message_id
                )
                reason = data.afk.get("reason")
                name = user.mention
                text = "『<i>User AFK</i>』 💤\n" f"├ User: {name}"
                if reason:
                    text += f"\n└ Reason: {reason}"
                else:
                    text += "\n└ Reason: Not specified"

                await self._client.bot.send_message(
                    chat_id=M.chat_id, text=text, reply_to_message_id=M.message_id, parse_mode="HTML",
                )

    async def _handle_afk_return(self, M: Message, user: User):
        now = datetime.now().timestamp()
        duration = self._client.utils.format_duration(int(now - user.afk["duration"]))
        text = (
            "『<i>Welcome Back</i>』 👋\n"
            f"├ User: {M.sender.mention}\n"
            f"└ Away For: {duration}"
        )
        msgs = user.afk.get("mentioned_msgs", [])
        if msgs:
            chat_id_clean = str(M.chat_id).replace("-100", "")
            text += "\n\n" "『<i>Tagged While Away</i>』 🔗"
            for i, msg_id in enumerate(msgs, 1):
                text += f"\n├ {i}. https://t.me/c/{chat_id_clean}/{msg_id}"
        await self._client.bot.send_message(
            chat_id=M.chat_id, text=text, parse_mode="HTML",reply_to_message_id=M.message_id
        )
        self._client.db.set_user_afk(M.sender.user_id, status=False)

    async def _validate_access(self, M: Message, cmd: BaseCommand) -> bool:
        cfg = cmd.config
        if getattr(cfg, "OnlyChat", False) and M.chat_type == "private":
            await M._client.bot.send_message(
                chat_id=M.chat_id,
                text=("『<i>Invalid Context</i>』 👥\n" "└ Group Only Command"),
                parse_mode="HTML",
            )
            return False

        if (
            getattr(cfg, "DevOnly", False)
            and M.sender.user_id not in self._client.config.mods
        ):
            await M._client.bot.send_message(
                chat_id=M.chat_id,
                text=("『<i>Access Denied</i>』 🚫\n" "└ Developer Only"),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return False

        if getattr(cfg, "OnlyAdmin", False):
            role, perms = await self._client.get_user_permissions(
                M.chat_id, M.sender.user_id
            )
            if role not in ["administrator", "creator"]:
                await M._client.bot.send_message(
                    chat_id=M.chat_id,
                    text=("『<i>Access Denied</i>』 ❌\n" "└ Admin Only"),
                    reply_to_message_id=M.message_id,
                )
                return False

            for req in getattr(cfg, "admin_permissions", []):
                if perms and not perms.get(req):
                    await M._client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "『<i>Permission Required</i>』 ⚠️\n"
                            f"└ Missing Permission: {req}"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    return False
        return True

    async def _process_xp(self, M: Message, user: User, amount: int):
        old_level_data = get_rank(user.xp)
        new_xp = user.xp + amount
        self._client.db.add_xp(M.sender.user_id, amount)
        new_level_data = get_rank(new_xp)

        if new_level_data["level"] > old_level_data["level"]:
            await M._client.bot.send_message(
                M.chat_id,
                (
                    "『<i>Level Up</i>』 🎉\n"
                    f"├ User: {M.sender.mention}\n"
                    f"└ Level: {new_level_data['level']}"
                ),
                parse_mode="HTML",
            )
