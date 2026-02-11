from __future__ import annotations

import os
from typing import Any, TYPE_CHECKING
from urllib.parse import quote_plus

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
                "command": "caption",
                "category": "fun",
                "description": {
                    "content": "Add a caption to an image or user avatar.",
                    "usage": "<reply> text:Hello bottom:true dark:true fontsize:30",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        text: str = flags.get("text") or context.get("text", "").strip()

        if not text:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❗ <b>『Missing Text』</b>\n"
                    "└ <i>Example: <code>/caption text:Hello World</code></i>"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
            return

        bottom: bool = flags.get("bottom", "false").lower() == "true"
        dark: bool = flags.get("dark", "true").lower() == "true"

        try:
            fontsize: int = int(flags.get("fontsize", 30))
        except (TypeError, ValueError):
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Invalid Font Size』</b>\n"
                    "└ <i>Use fontsize:&lt;number&gt;</i>"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
            return

        image_url: str

        if M.reply_to_message and M.reply_to_message.photo:
            file_id: str = M.reply_to_message.photo[-1].file_id
            path: str = await self.client.download_media(file_id)
            image_url = self.client.utils.img_to_url(path)
            os.remove(path)
        else:
            user = (
                M.reply_to_user
                or (M.mentioned[0] if M.mentioned else None)
                or M.sender
            )
            image_url = await self.client.profile_photo_url(user.user_id)

        api_url: str = (
            "https://api.popcat.xyz/v2/caption"
            f"?image={quote_plus(image_url)}"
            f"&text={quote_plus(text)}"
            f"&bottom={str(bottom).lower()}"
            f"&dark={str(dark).lower()}"
            f"&fontsize={fontsize}"
        )

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=api_url,
            reply_to_message_id=M.message_id,
        )