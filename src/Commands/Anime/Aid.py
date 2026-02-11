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
                "command": "aid",
                "aliases": ["animeid"],
                "category": "anime",
                "description": {
                    "content": "Get detailed info of anime by ID.",
                    "usage": "<anime_id>",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        raw_id: str = context.get("text", "")
    
        if not raw_id.isdigit():
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Invalid ID』</b>\n"
                    "└ <i>You must provide a valid anime ID.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        anime_id: int = int(raw_id)
    
        try:
            data = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/anime?search={anime_id}"
            )
    
            if not data:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 <b>『Not Found』</b>\n"
                        "└ <i>No anime found for this ID.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            anime: dict[str, Any] = data[0]
            title: dict[str, str] = anime.get("title", {})
    
            trailer_id: str | None = anime.get("trailer", {}).get("id")
            trailer_url: str = (
                f"https://youtu.be/{trailer_id}" if trailer_id else "N/A"
            )
    
            text: str = (
                "<blockquote>"
                f"🎬 <b>『{title.get('english') or title.get('romaji') or 'Unknown'}』</b>\n"
                f"├ <b>Romaji:</b> {title.get('romaji') or '—'}\n"
                f"├ <b>Japanese:</b> {title.get('native') or '—'}\n"
                f"├ <b>Type:</b> {anime.get('format') or '—'}\n"
                f"├ <b>Adult:</b> {'Yes' if anime.get('isAdult') else 'No'}\n"
                f"├ <b>Status:</b> {anime.get('status') or '—'}\n"
                f"├ <b>Episodes:</b> {anime.get('episodes') or '—'}\n"
                f"├ <b>Duration:</b> {anime.get('duration') or '—'} min\n"
                f"├ <b>First Aired:</b> {anime.get('startDate') or '—'}\n"
                f"├ <b>Last Aired:</b> {anime.get('endDate') or '—'}\n"
                f"├ <b>Genres:</b> {', '.join(anime.get('genres', [])) or '—'}\n"
                f"├ <b>Studios:</b> {anime.get('studios') or '—'}\n"
                f"└ <b>Trailer:</b> {trailer_url}\n\n"
                f"📖 <b>『Description』</b>\n"
                f"{anime.get('description') or 'No description available.'}"
                "</blockquote>"
            )
    
            image = await self.client.utils.fetch_buffer(anime["imageUrl"])
    
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
                    "└ <i>Failed to fetch anime data.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            self.client.log.error(f"[ERROR] {e.__traceback__.tb_lineno}: {e}")
                
    