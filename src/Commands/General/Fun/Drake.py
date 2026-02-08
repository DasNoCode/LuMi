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
                "command": "drake",
                "category": "fun",
                "description": {
                    "content": "Create a Drake meme.",
                    "usage": "text1:<no> text2:<yes> or reply to text",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        reply = M.reply_to_message

        text1: str | None = flags.get("text1")
        text2: str | None = flags.get("text2")

        if reply and reply.text and not text2:
            text2 = reply.text.strip()

        if not text1 or not text2:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ Usage: /drake text1:<no> text2:<yes> (or reply to text)",
                reply_to_message_id=M.message_id,
            )
            return

        url: str = (
            "https://api.popcat.xyz/v2/drake"
            f"?text1={quote_plus(text1)}"
            f"&text2={quote_plus(text2)}"
        )

        await self.client.send_photo(
            chat_id=M.chat_id,
            photo=url,
            reply_to_message_id=M.message_id,
        )