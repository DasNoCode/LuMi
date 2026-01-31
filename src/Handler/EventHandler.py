from __future__ import annotations
from typing import Any
from telegram import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, User


class EventHandler:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def handler(self, M: Any) -> None:
        if not M.is_event:
            return

        chat_data = self._client.db.get_group_by_chat_id(M.chat_id)
        events_on: bool = bool(getattr(chat_data, "events", False))
        captcha_on: bool = bool(getattr(chat_data, "captcha", False))

        if not events_on:
            return
        
        await self._client.bot.delete_message(
            chat_id=M.chat_id,
            message_id=M.message_id,
        )
        
        if M.event_type == "join":
            user: User = M.event_user
            name: str = user.user_name or user.user_full_name
            is_added: bool = bool(M.action_by)

            if captcha_on and not is_added:
                try:
                    await self._client.bot.restrict_chat_member(
                        chat_id=M.chat_id,
                        user_id=user.user_id,
                        permissions=ChatPermissions.no_permissions(),
                    )
                except Exception as e:
                    self._client.log.error(f"[Captcha Restrict Error] {e}")

                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🔐 Verify Captcha",
                                callback_data=f"cmd:captcha type:captcha user_id:{user.user_id}",
                            )
                        ]
                    ]
                )

                text: str = (
                    f"👋 @{name}\n"
                    f"Before you start chatting, please verify you are human.\n"
                    f"Tap the button below 👇"
                )

                await self._client.send_message(
                    chat_id=M.chat_id, text=text, reply_markup=keyboard
                )
                return

            if is_added:
                by: str = M.action_by.user_name or M.action_by.user_full_name
                text = f"👋 @{name} was added by @{by}"
            else:
                text = f"👋 @{name} joined the chat."

            await self._client.send_message(chat_id=M.chat_id, text=text)
            return

        if M.event_type == "leave":
            name: str = M.event_user.user_name or M.event_user.user_full_name
            await self._client.send_message(
                chat_id=M.chat_id, text=f"👋 @{name} left the chat."
            )
            return

        if M.event_type == "kick":
            name: str = M.event_user.user_name or M.event_user.user_full_name
            by: str = M.action_by.user_name or M.action_by.user_full_name
            await self._client.send_message(
                chat_id=M.chat_id, text=f"❌ @{name} was removed by @{by}."
            )
            return
