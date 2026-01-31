from __future__ import annotations

import asyncio
from typing import Any, TYPE_CHECKING, Dict, Tuple

from Libs import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from Commands.ChatCmds.Captcha.Utils import CaptchaUtils

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
                "category": "general",
                "OnlyChat": True,
            },
        )

    async def exec(self, message: Message, context: Dict[str, Any]) -> None:
        if not message.is_callback:
            return

        await self.client.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id,
        )

        flags: Dict[str, Any] = context.get("flags", {})
        user_id: int = int(flags.get("user_id", 0))

        if not user_id:
            return

        key: Tuple[int, int] = (message.chat_id, user_id)
        existing: Dict[str, Any] | None = self.client.captcha_store.get(key)

        captcha_code: str = CaptchaUtils.random_text()
        options: list[str] = CaptchaUtils.captcha_options(captcha_code)

        self.client.captcha_store[key] = {
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

        sent_message = await self.client.send_photo(
            chat_id=message.chat_id,
            photo=CaptchaUtils.captcha_image(captcha_code),
            caption="🔐 Solve the captcha within 3 minutes.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        asyncio.create_task(
            self._expire_after(
                chat_id=message.chat_id,
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

        key: Tuple[int, int] = (chat_id, user_id)
        captcha_data: Dict[str, Any] | None = self.client.captcha_store.get(key)

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
            self.client.captcha_store.pop(key, None)
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
            await self.client.send_message(
                chat_id=chat_id,
                text="⏳ Captcha expired.\nPlease retry within 3 minutes.",
                reply_markup=retry_markup,
            )
        except Exception:
            pass
