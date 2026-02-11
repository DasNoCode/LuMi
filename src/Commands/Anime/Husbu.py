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
            res: dict[str, Any] = await self.client.utils.fetch(
                "https://nekos.best/api/v2/husbando"
            )
    
            results: list[dict[str, Any]] = res.get("results", [])
    
            if not results:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❌ <b>『Unavailable』</b>\n"
                        "└ <i>No husbando found right now.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            data: dict[str, Any] = results[0]
    
            image = await self.client.utils.fetch_buffer(data.get("url"))
    
            text: str = (
                "<blockquote>"
                "🧔 <b>『Husbando』</b>\n"
                f"├ <b>Source:</b> {data.get('source_url') or 'N/A'}\n"
                f"├ <b>Artist Profile:</b> {data.get('artist_href') or 'N/A'}\n"
                f"└ <b>Image URL:</b> {data.get('url') or 'N/A'}"
                "</blockquote>"
            )
    
            await self.client.bot.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
    
        except Exception:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『Error』</b>\n"
                    "└ <i>Failed to fetch husbando image.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            self.client.log.error(f"[ERROR]\n{traceback.format_exc()}")




            