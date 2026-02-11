from __future__ import annotations

import os
import traceback
from typing import Any, TYPE_CHECKING

from telegram.error import NetworkError
from Libs import BaseCommand


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "setchatpfp",
                "aliases": ["setpfp", "setgpic"],
                "category": "chat",
                "description": {
                    "content": "Set a new chat profile photo (reply to an image or send it with caption).",
                    "usage": "<reply to a photo or send with caption>",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_change_info"],
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            photo_file_id: str | None = None

            if M.msg_type == "photo" and M.file_id:
                photo_file_id = M.file_id
            elif (
                M.reply_to_message
                and M.reply_to_message.photo
                and M.reply_to_message.photo[0].file_id
            ):
                photo_file_id = M.reply_to_message.photo[0].file_id

            if not photo_file_id:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❗ <b>『Invalid Usage』</b>\n"
                        "└ <i>Reply to a photo or send one with the command.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            loading = await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="👨‍💻",
                reply_to_message_id=M.message_id,
            )

            path: str | None = None

            try:
                path = await self.client.download_media(photo_file_id)

                with open(path, "rb") as img:
                    await self.client.bot.set_chat_photo(
                        chat_id=M.chat_id,
                        photo=img,
                    )

                await self.client.bot.delete_message(
                    chat_id=M.chat_id,
                    message_id=loading.message_id,
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🖼️ <b>『Chat Photo Updated』</b>\n"
                        "└ <i>Group profile picture updated successfully.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )

            finally:
                if path and os.path.exists(path):
                    os.remove(path)

        except NetworkError as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『Network Error』</b>\n"
                    "└ <i>Telegram network issue. Please try again.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )

        except Exception as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Error』</b>\n"
                    "└ <i>Something went wrong. Please try again later.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )