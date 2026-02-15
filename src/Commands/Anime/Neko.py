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
                "command": "neko",
                "aliases": ["catgirl"],
                "category": "anime",
                "description": {"content": "Send a cute neko image."},
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            res: dict[str, Any] = await self.client.utils.fetch(
                "https://nekos.best/api/v2/neko"
            )
    
            results: list[dict[str, Any]] = res.get("results", [])
    
            if not results:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❌ <b>『Unavailable』</b>\n"
                        "└ <i>No neko found right now.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            neko: dict[str, Any] = results[0]
    
            image = await self.client.utils.fetch_buffer(neko.get("url"))
    
            caption: str = (
                "<blockquote>"
                "🐾 <b>『Neko』</b>\n"
                f"├ <b>Artist:</b> {neko.get('artist_name') or 'Unknown'}\n"
                f"├ <b>Source:</b> {neko.get('source_url') or 'N/A'}\n"
                f"├ <b>Artist Profile:</b> {neko.get('artist_href') or 'N/A'}\n"
                f"└ <b>Image URL:</b> {neko.get('url') or 'N/A'}"
                "</blockquote>"
            )
    
            await self.client.bot.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=caption,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
    
        except Exception as e:
            error = self.client.utils.format_execution_error(e=e, file_filter=__file__)
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=error,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
    