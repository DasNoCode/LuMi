from __future__ import annotations

from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
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
                "command": "start",
                "category": "general",
                "description": {
                    "content": "Start the bot and see introduction.",
                    "usage": "",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🧑‍💻 Owner",
                        url="https://t.me/OWNER_USERNAME",
                    ),
                    InlineKeyboardButton(
                        "💬 Support",
                        url="https://t.me/SUPPORT_GROUP",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "➕ Add to Group",
                        url=f"https://t.me/{self.client.bot.username}?startgroup=true",
                    ),
                    InlineKeyboardButton(
                        "🤖 Commands List",
                        callback_data="cmd:Commands",
                    ),
                ],
            ]
        )

        text = (
            "👋 <b>Hello, I'm Lumi!</b>\n\n"
            "Chat with me anytime! 💬\n"
            "Let's talk, share moments, and have some fun together ✨"
        )

        await self.client.send_message(
            chat_id=M.chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
