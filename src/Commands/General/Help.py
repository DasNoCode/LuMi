from __future__ import annotations
from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from telegram.constants import ParseMode

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler

class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "help",
                "aliases": ["cmds", "commands"],
                "category": "general",
                "description": {
                    "content": "List all available commands and their usage.",
                    "usage": "[command_name]",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            cmd_arg = context.get("text", "").strip().lower()
            if cmd_arg:
                target = self.handler._commands.get(cmd_arg)
                if target and target.config.get("visible", True):
                    desc = target.config.get("description", {})
                    text = (
                        "『<i>Command Info</i>』 📖\n"
                        f"├ <i>Command</i>: <code>{target.config.command}</code>\n"
                        f"├ <i>Category</i>: {target.config.get('category', 'None')}\n"
                        f"├ <i>Usage</i>: {self.client.prefix}{target.config.command} {desc.get('usage', '')}\n"
                        f"└ <i>Description</i>: {desc.get('content', 'No description available.')}"
                    )
                    return await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=M.message_id,
                    )
                    
            category_emojis = {
                "fun": "👾『Fun』👾",
                "chat": "👥『Chat』👥",
                "anime": "🍥『Anime』🍥",
                "game": "🎯『Game』🎯",
                "general": "✨『General』✨",
                "sticker": "🧑‍🎨『Sticker』🧑‍🎨",
                "search": "🔍『Search』🔍",
            }

            categories = {}
            for cmd in self.handler._commands.values():
                if not cmd.config.get("visible", True):
                    continue
                
                cat = cmd.config.get("category", "uncategorized").lower()
                categories.setdefault(cat, []).append(f"<code>{cmd.config.command}</code>")

            # Build the menu string
            lines = ["『<i>Available Commands</i>』\n"]
            for cat in sorted(categories.keys()):
                title = category_emojis.get(cat, f"『<i>{cat.capitalize()}</i>』")
                cmds_list = ", ".join(sorted(categories[cat]))
                lines.append(f"{title}\n└ {cmds_list}\n")

            lines.append(f"Use <code>{self.client.prefix}help [command]</code> for details.")

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="\n".join(lines),
                parse_mode=ParseMode.HTML,
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            error = self.client.utils.format_execution_error(e=e, file_filter=__file__)
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=error,
                reply_to_message_id=M.message_id,
                parse_mode=ParseMode.HTML,
            )
