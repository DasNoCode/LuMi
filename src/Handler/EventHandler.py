from __future__ import annotations

import traceback
from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.constants import ParseMode


class EventHandler:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def handler(self, M: Any) -> None:
        if not M.is_event:
            return

        # Bot added to group
        if (
            M.event_type == "join"
            and M.event_user.user_id == self._client.bot_user_id
        ):
            return await self._bot_joined_group(M.chat_id)

        chat_data = self._client.db.get_group_by_chat_id(M.chat_id)

        if not getattr(chat_data, "events", False):
            return

        try:
            await self._client.bot.delete_message(M.chat_id, M.message_id)
        except Exception:
            pass

        text: str | None = None

        if M.event_type == "join":
            if getattr(chat_data, "captcha", False) and not M.action_by:
                return await self._send_captcha(M)

            if M.action_by:
                text = (
                    "『<i>User Added</i>』👋\n"
                    f"├ <i>User</i>: {M.event_user.mention}\n"
                    f"└ <i>Added By</i>: {M.action_by.mention}"
                )
            else:
                text = (
                    "『<i>User Joined</i>』👋\n"
                    f"└ <i>User</i>: {M.event_user.mention}"
                )

        elif M.event_type == "leave":
            text = (
                "『<i>User Left</i>』🚪\n"
                f"└ <i>User</i>: {M.event_user.mention}"
            )

        elif M.event_type == "kick":
            text = (
                "『<i>User Removed</i>』❌\n"
                f"├ <i>User</i>: {M.event_user.mention}\n"
                f"└ <i>Removed By</i>: {M.action_by.mention if M.action_by else 'Admin'}"
            )

        if text:
            msg = await self._client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
            )

    async def _send_captcha(self, M: Any) -> None:
        try:
            await self._client.bot.restrict_chat_member(
                M.chat_id,
                M.event_user.user_id,
                ChatPermissions.no_permissions(),
            )
        except Exception as e:
            self._client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "『Verify Captcha』",
                        callback_data=(
                            f"cmd:captcha user_id:{M.event_user.user_id}"
                        ),
                    )
                ]
            ]
        )

        text: str = (
            "『<i>Verification Required</i>』🔐\n"
            f"├ <i>User</i>: {M.event_user.mention}\n"
            "└ <i>Action</i>: Please verify to start chatting."
        )

        await self._client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )

    async def _bot_joined_group(self, chat_id: int) -> None:
        role, _ = await self._client.get_user_permissions(
            chat_id=chat_id,
            user_id=self._client.bot_user_id,
        )
        
        requirement_line: str = (
            "├ <i>Requirement</i>: Promote me to Admin\n"
            if role not in ("administrator", "creator")
            else ""
        )
        
        text: str = (
            "『<i>Introduction</i>』🤖\n"
            f"├ <i>Name</i>: {self._client.bot_name}\n"
            f"{requirement_line}"
            f"└ <i>Help</i>: Use {self._client.prefix}help"
        )

        await self._client.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )