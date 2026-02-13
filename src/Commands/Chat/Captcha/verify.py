from __future__ import annotations

import asyncio
from typing import Any, TYPE_CHECKING, Dict, Tuple
from telegram import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from Libs import BaseCommand


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    _retry_guard: Dict[Tuple[str, int, int], bool] = {}

    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "verify",
                "category": "chat",
                "OnlyChat": True,
            },
        )

    async def exec(self, M: Message, context: Dict[str, Any]) -> None:
        if not M.is_callback:
            return

        flags: Dict[str, Any] = context.get("flags", {})
        user_id: int = int(flags.get("user_id", 0))
        value: str = str(flags.get("val", ""))

        if not user_id or not value:
            return

        key: Tuple[str, int, int] = ("captcha", M.chat_id, user_id)

        captcha_data: Dict[str, Any] | None = (
            self.client.interaction_store.get(key)
        )
        if not captcha_data:
            return

        self._retry_guard.pop(key, None)

        clicker_id: int = M.sender.user_id
        if clicker_id != user_id:
            permissions: Dict[str, bool] | None = M.sender.permissions
            if not permissions or not permissions.get("can_restrict_members"):
                return

        attempt: int = int(captcha_data["attempt"])

        if value == captcha_data["code"]:
            self.client.interaction_store.pop(key, None)

            await self.client.bot.restrict_chat_member(
                chat_id=M.chat_id,
                user_id=user_id,
                permissions=ChatPermissions.all_permissions(),
            )

            await self.client.bot.delete_message(
                chat_id=M.chat_id,
                message_id=M.message_id,
            )

            text: str = (
                "『<i>Verified</i>』✅\n"
                f"└ <i>User</i>: {M.sender.mention}"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode="HTML",
            )
            return

        if attempt >= 2:
            self.client.interaction_store.pop(key, None)

            await self.client.kick_chat_member(
                chat_id=M.chat_id,
                user_id=user_id,
            )

            try:
                text: str = (
                    "『<i>Captcha Failed</i>』❌\n"
                    "└ <i>Status</i>: User kicked"
                )

                await self.client.bot.edit_message_caption(
                    chat_id=M.chat_id,
                    message_id=M.message_id,
                    caption=text,
                    reply_markup=None,
                    parse_mode="HTML",
                )
            except Exception:
                pass

            return

        captcha_data["attempt"] = attempt + 1

        retry_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="『Retry captcha』",
                        callback_data=f"cmd:captcha user_id:{user_id}",
                    )
                ]
            ]
        )

        text: str = (
            "『<i>Incorrect Captcha</i>』❌\n"
            "└ <i>Action</i>: Retry within 3 minutes"
        )

        await self.client.bot.edit_message_caption(
            chat_id=M.chat_id,
            message_id=M.message_id,
            caption=text,
            reply_markup=retry_markup,
            parse_mode="HTML",
        )

        self._retry_guard[key] = True

        asyncio.create_task(
            self._retry_expire(
                chat_id=M.chat_id,
                message_id=M.message_id,
                user_id=user_id,
            )
        )

    async def _retry_expire(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
    ) -> None:
        await asyncio.sleep(180)

        key: Tuple[str, int, int] = ("captcha", chat_id, user_id)

        if key not in self._retry_guard:
            return

        self._retry_guard.pop(key, None)
        self.client.interaction_store.pop(key, None)

        try:
            await self.client.kick_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            text: str = (
                "『<i>Retry Expired</i>』⏰\n"
                "└ <i>Status</i>: User kicked"
            )

            await self.client.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=text,
                reply_markup=None,
                parse_mode="HTML",
            )
        except Exception:
            pass