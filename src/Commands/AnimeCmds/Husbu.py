from __future__ import annotations
from Libs import BaseCommand
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "husbu",
                "aliases": ["husbando"],
                "category": "anime",
                "description": {
                    "content": "Send a husbando image.",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            res = self.client.utils.fetch("https://nekos.best/api/v2/husbando")
            results = res.get("results", [])

            if not results:
                return await self.client.send_message(
                    M.chat_id,
                    "❌ Couldn't find a husbando image right now. Try again later.",
                    reply_to_message_id=M.message_id,
                )

            husbando = results[0]
            image = self.client.utils.fetch_buffer(husbando["url"])

            msg = (
                f"🧔 Here's a Husbando for you!\n"
                f"🎨 Artist: {husbando['artist_name']}\n"
                f"🔗 Source: {husbando['source_url']}\n"
                f"👤 Artist Profile: {husbando['artist_href']}\n"
                f"🖼 Image: {husbando['url']}"
            )

            await self.client.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=msg,
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch husbando image.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [Husbando] {e}")
