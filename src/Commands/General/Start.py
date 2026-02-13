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
        if M.is_callback:
            try:
                text: str = (
                    "『<i>Introduction</i>』👤\n"
                    f"├ <i>Name</i>: LuMi\n"
                    f"├ <i>User</i>: {M.sender.mention}\n"
                    "└ <i>Description</i>: A group management bot with games and anime commands"
                )

                await self.client.bot.edit_message_caption(
                    chat_id=M.chat_id,
                    message_id=M.message_id,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "『Owner』🧑‍💻",
                                    url="https://t.me/OWNER_USERNAME",
                                ),
                                InlineKeyboardButton(
                                    "『Support』💬 ",
                                    url="https://t.me/SUPPORT_GROUP",
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    "『Add to Group』➕ ",
                                    url=f"https://t.me/{self.client.bot.username}?startgroup=true",
                                ),
                                InlineKeyboardButton(
                                    "『Commands List』🤖",
                                    callback_data="cmd:Commands",
                                ),
                            ],
                        ]
                    ),
                )
            except Exception:
                pass
            return

        text: str = (
            "『<i>Hello</i>』👋\n"
            f"└ <i>User</i>: {M.sender.mention}"
        )

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo="src/Assets/bot_image.jpg",
            caption=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "『Hello』👋 ",
                            callback_data="cmd:start",
                        ),
                        InlineKeyboardButton(
                            "『Intro』✨ ",
                            callback_data="cmd:start intro:true",
                        ),
                    ]
                ]
            ),
        )