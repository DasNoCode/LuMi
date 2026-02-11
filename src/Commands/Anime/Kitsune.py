from __future__ import annotations
import traceback
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
            res: dict[str, Any] = await self.client.utils.fetch(
                "https://nekos.best/api/v2/kitsune"
            )
    
            results: list[dict[str, Any]] = res.get("results", [])
    
            if not results:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❌ <b>『Unavailable』</b>\n"
                        "└ <i>No kitsune found right now.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            kitsune: dict[str, Any] = results[0]
    
            image = await self.client.utils.fetch_buffer(kitsune.get("url"))
    
            text: str = (
                "<blockquote>"
                "🦊 <b>『Kitsune』</b>\n"
                f"├ <b>Artist:</b> {kitsune.get('artist_name') or 'Unknown'}\n"
                f"├ <b>Source:</b> {kitsune.get('source_url') or 'N/A'}\n"
                f"├ <b>Artist Profile:</b> {kitsune.get('artist_href') or 'N/A'}\n"
                f"└ <b>Image URL:</b> {kitsune.get('url') or 'N/A'}"
                "</blockquote>"
            )
    
            await self.client.bot.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
    
        except Exception as e:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『Error』</b>\n"
                    "└ <i>Failed to fetch kitsune image.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            self.client.log.error(f"[ERROR] {e.__traceback__.tb_lineno}: {e}")