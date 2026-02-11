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
        user_mention: str = M.sender.user_name or M.sender.user_full_name

        if M.is_callback:
            try:
                await self.client.bot.edit_message_caption(
                    chat_id=M.chat_id,
                    message_id=M.message_id,
                    caption=(
                        "✨ <b>『Welcome』</b>\n"
                        f"├ <b>User:</b> {user_mention}\n"
                        "├ <b>Name:</b> LuMi\n"
                        "└ <i>Your all-in-one group management bot "
                        "with fun games and anime commands!</i>"
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(
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
                    ),
                )
            except Exception:
                pass
            return

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo="src/Assets/bot_image.jpg",
            caption=(
                "👋 <b>『Hello』</b>\n"
                f"├ <b>User:</b> {user_mention}\n"
                "└ <i>Tap below to explore Lumi ✨</i>"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "👋 Hello",
                            callback_data="cmd:start",
                        ),
                        InlineKeyboardButton(
                            "✨ Intro",
                            callback_data="cmd:start intro:true",
                        ),
                    ]
                ]
            ),
        )