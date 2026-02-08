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
                "command": "alert",
                "category": "fun",
                "description": {
                    "content": "Generate a PopCat alert image.",
                    "usage": "<text>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        text: str = context.get("text", "").strip()

        if not text:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ Please provide some text for the alert.",
                reply_to_message_id=M.message_id,
            )
            return

        encoded: str = quote_plus(text)
        url: str = f"https://api.popcat.xyz/v2/alert?text={encoded}"

        await self.client.send_photo(
            chat_id=M.chat_id,
            photo=url,
            reply_to_message_id=M.message_id,
        )