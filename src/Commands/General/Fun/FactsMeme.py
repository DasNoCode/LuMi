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
                "command": "facts",
                "aliases": ["fact"],
                "category": "fun",
                "description": {
                    "content": "Generate a fun fact image.",
                    "usage": "<text>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        text: str = " ".join(context.get("text", [])).strip()

        if not text:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ Please provide some text for the fact.",
                reply_to_message_id=M.message_id,
            )
            return

        query: str = quote_plus(text)
        image_url: str = f"https://api.popcat.xyz/v2/facts?text={query}"

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=image_url,
            reply_to_message_id=M.message_id,
        )