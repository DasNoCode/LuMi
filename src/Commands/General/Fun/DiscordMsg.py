from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote_plus
from datetime import datetime, timezone

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
                "command": "discord",
                "category": "fun",
                "description": {
                    "content": "Generate a Discord-style message sticker.",
                    "usage": "<text> or reply to text [color:#ffcc99]",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        text: list[str] = context.get("text", [])

        reply = M.reply_to_message

        if reply and reply.text:
            content: str = reply.text.strip()
            user = M.reply_to_user
        else:
            content = " ".join(text).strip()
            user = (
                M.reply_to_user
                or (M.mentions[0] if M.mentions else None)
                or M.sender
            )

        if not content:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ Please provide text or reply to a message.",
                reply_to_message_id=M.message_id,
            )
            return

        username: str = user.user_name or user.user_full_name or "User"
        avatar_url: str = await self.client.db.profile_to_url(user.user_id)

        color: str = flags.get("color", "#ffcc99")
        timestamp: str = datetime.now(timezone.utc).isoformat(timespec="seconds")

        api_url: str = (
            "https://api.popcat.xyz/v2/discord-message"
            f"?username={quote_plus(username)}"
            f"&content={quote_plus(content)}"
            f"&avatar={quote_plus(avatar_url)}"
            f"&color={quote_plus(color)}"
            f"&timestamp={quote_plus(timestamp)}"
        )

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=api_url,
            reply_to_message_id=M.message_id,
        )