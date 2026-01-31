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
                "command": "waifu",
                "aliases": ["wife"],
                "category": "anime",
                "description": {"content": "Send a random waifu image."},
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            res = self.client.utils.fetch("https://nekos.best/api/v2/waifu")
            results = res.get("results", [])

            if not results:
                return await self.client.send_message(
                    M.chat_id,
                    "❌ Couldn't find a waifu image right now. Try again later.",
                    reply_to_message_id=M.message_id,
                )

            waifu = results[0]
            image = self.client.utils.fetch_buffer(waifu["url"])

            message = f"""💖 Here's a Waifu for you!
                    🎨 Artist: {waifu['artist_name']}
                    🔗 Source: {waifu['source_url']}
                    👤 Artist Profile: {waifu['artist_href']}
                    🖼 Image: {waifu['url']}"""

            await self.client.send_image(
                M.chat_id,
                image,
                message.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch waifu image.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [Waifu] {e}")
