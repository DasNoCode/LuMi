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
                "command": "kitsune",
                "aliases": ["foxgirl"],
                "category": "anime",
                "description": {
                    "content": "Send a cute kitsune image.",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            res = self.client.utils.fetch("https://nekos.best/api/v2/kitsune")
            results = res.get("results", [])

            if not results:
                return await self.client.send_message(
                    M.chat_id,
                    "❌ Couldn't find a kitsune image right now. Try again later.",
                    reply_to_message_id=M.message_id,
                )

            kitsune = results[0]
            image = self.client.utils.fetch_buffer(kitsune["url"])

            msg = (
                f"🦊 Here's a Kitsune for you!\n"
                f"🎨 Artist: {kitsune['artist_name']}\n"
                f"🔗 Source: {kitsune['source_url']}\n"
                f"👤 Artist Profile: {kitsune['artist_href']}\n"
                f"🖼 Image: {kitsune['url']}"
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
                "⚠️ Failed to fetch kitsune image.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [Kitsune] {e}")
