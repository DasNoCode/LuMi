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
                "command": "neko",
                "aliases": ["catgirl"],
                "category": "anime",
                "description": {"content": "Send a cute neko image."},
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            res = self.client.utils.fetch("https://nekos.best/api/v2/neko")
            results = res.get("results", [])

            if not results:
                return await self.client.send_message(
                    M.chat_id,
                    "❌ Couldn't find a neko image right now. Try again later.",
                    reply_to_message_id=M.message_id,
                )

            neko = results[0]
            image = self.client.utils.fetch_buffer(neko["url"])

            message = f"""🐾 Here's a Neko for you!
                    🎨 Artist: {neko['artist_name']}
                    🔗 Source: {neko['source_url']}
                    👤 Artist Profile: {neko['artist_href']}
                    🖼 Image: {neko['url']}"""

            await self.client.send_image(
                M.chat_id,
                image,
                message.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch neko image.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [Neko] {e}")
