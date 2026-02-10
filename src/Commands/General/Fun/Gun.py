from __future__ import annotations

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
                "command": "gun",
                "category": "fun",
                "description": {
                    "content": "Generate a gun meme image.",
                    "usage": "<reply | @user> text:pet me or die",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        raw_text: str = context.get("text", "").strip()
        text: str = flags.get("text") or raw_text or "pet me or die"

        image_url: str

        if M.reply_to_message and M.reply_to_message.photo:
            file_id = M.reply_to_message.photo[-1].file_id
            path = await self.client.download_media(file_id)
            image_url = self.client.utils.img_to_url(path)

        else:
            user = (
                M.reply_to_user
                or (M.mentioned[0] if M.mentioned else None)
                or M.sender
            )
            image_url = await self.client.profile_photo_url(user.user_id)

        api_url: str = (
            "https://api.popcat.xyz/v2/gun"
            f"?image={quote_plus(image_url)}"
            f"&text={quote_plus(text)}"
        )

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=api_url,
            reply_to_message_id=M.message_id,
        )