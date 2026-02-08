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
                "command": "ad",
                "category": "fun",
                "description": {
                    "content": "Generate an advertisement image using a photo or user avatar.",
                    "usage": "<reply to photo | reply / @user>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
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

        ad_url: str = (
            "https://api.popcat.xyz/v2/ad"
            f"?image={quote_plus(image_url)}"
        )

        await self.client.send_photo(
            chat_id=M.chat_id,
            photo=ad_url,
            reply_to_message_id=M.message_id,
        )