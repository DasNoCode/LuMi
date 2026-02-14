from __future__ import annotations

import asyncio
from Libs import BaseCommand
from typing import Any, TYPE_CHECKING, Dict, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "captcha",
                "category": "Chat",
                "OnlyChat": True,
                "visible": False
            },
        )

    async def exec(self, M: Message, context: Dict[str, Any]) -> None:
        if not M.is_callback:
            return

        await self.client.bot.delete_message(
            chat_id=M.chat_id,
            message_id=M.message_id,
        )

        loading = await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="🔑",
        )

        flags: Dict[str, Any] = context.get("flags", {})
        user_id: int = int(flags.get("user_id", 0))

        if not user_id:
            return

        key: Tuple[str, int, int] = ("captcha", M.chat_id, user_id)
        existing: Dict[str, Any] | None = self.client.interaction_store.get(key)

        captcha_code: str = self.client.utils.random_text()
        options: list[str] = self.client.utils.captcha_options(captcha_code)

        self.client.interaction_store[key] = {
            "code": captcha_code,
            "attempt": existing["attempt"] if existing else 1,
        }

        keyboard: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text=options[i],
                    callback_data=f"cmd:verify val:{options[i]} user_id:{user_id}",
                ),
                InlineKeyboardButton(
                    text=options[i + 1],
                    callback_data=f"cmd:verify val:{options[i + 1]} user_id:{user_id}",
                ),
            ]
            for i in range(0, 4, 2)
        ]

        await self.client.bot.delete_message(
            chat_id=M.chat_id,
            message_id=loading.message_id,
        )

        sent_message = await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=self.client.utils.captcha_image(captcha_code),
            caption=(
                "🔐 <b>『Captcha Verification』</b>\n"
                "└ <i>Solve the captcha within 3 minutes.</i>"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

        asyncio.create_task(
            self._expire_after(
                chat_id=M.chat_id,
                message_id=sent_message.message_id,
                user_id=user_id,
            )
        )

    async def _expire_after(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
    ) -> None:
        await asyncio.sleep(180)

        key: Tuple[str, int, int] = ("captcha", chat_id, user_id)
        captcha_data: Dict[str, Any] | None = self.client.interaction_store.get(key)

        if not captcha_data:
            return

        attempt: int = int(captcha_data["attempt"])

        try:
            await self.client.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            pass

        if attempt >= 2:
            self.client.interaction_store.pop(key, None)
            try:
                await self.client.kick_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                )
            except Exception:
                pass
            return

        captcha_data["attempt"] = attempt + 1

        retry_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🔁 Retry captcha",
                        callback_data=f"cmd:captcha user_id:{user_id}",
                    )
                ]
            ]
        )

        try:
            await self.client.bot.send_message(
                chat_id=chat_id,
                text=(
                    "⏳ <b>『Captcha Expired』</b>\n"
                    "└ <i>Please retry within 3 minutes.</i>"
                ),
                reply_markup=retry_markup,
                parse_mode="HTML",
            )
        except Exception:
            pass