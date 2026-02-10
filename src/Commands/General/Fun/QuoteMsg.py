from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING
from urllib.parse import quote

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
                "command": "dmsg",
                "category": "fun",
                "description": {
                    "content": "Generate a Discord-style message image.",
                    "usage": "<reply to user> color:#ffcc99",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        reply = M.reply_to_user
        if not reply or not M.reply_to_message.text:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ Reply to a user to generate the message.",
                reply_to_message_id=M.message_id,
            )
            return

        flags: dict[str, str] = context.get("flags", {})
        color: str = flags.get("color", "#ffcc99")

        username: str = reply.user_name
        photo_id: str = (await self.client.get_profile_id(reply.user_id))
        if photo_id:
            photo = await self.client.download_media(photo_id)
        avatar_url: str = self.client.utils.img_to_url(photo) or self.client.utils.img_to_url("src/Assets/image.png")
        os.remove(photo)

        timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        url: str = (
            "https://api.popcat.xyz/v2/discord-message?"
            f"username={quote(username)}"
            f"&content={quote(M.reply_to_message.text)}"
            f"&avatar={quote(avatar_url)}"
            f"&color={quote(color)}"
            f"&timestamp={quote(timestamp)}"
        )
        photo = Path(self.client.utils.fetch_buffer(url))
        webm = self.client.utils.image_to_webp(photo, photo.with_suffix(".webp"))
        await self.client.bot.send_sticker(
            chat_id=M.chat_id,
            sticker=webm,
            reply_to_message_id=M.message_id,
        )
