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
                "command": "mid",
                "aliases": ["mangaid"],
                "category": "anime",
                "description": {
                    "content": "Get detailed info of a manga using its ID.",
                    "usage": "<manga_id>",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        raw_id: str = context.get("text", "").strip()
    
        if not raw_id.isdigit():
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Invalid ID』</b>\n"
                    "└ <i>You must provide a valid manga ID.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        manga_id: int = int(raw_id)
    
        try:
            results: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/manga?search={manga_id}"
            )
    
            if not results:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 <b>『Not Found』</b>\n"
                        "└ <i>No manga found for this ID.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            manga: dict[str, Any] = results[0]
            title: dict[str, str] = manga.get("title", {})
    
            trailer_id: str | None = (
                manga.get("trailer", {}) or {}
            ).get("id")
    
            trailer_url: str = (
                f"https://youtu.be/{trailer_id}" if trailer_id else "N/A"
            )
    
            text: str = (
                "<blockquote>"
                f"📚 <b>『{title.get('english') or title.get('romaji') or 'Unknown'}』</b>\n"
                f"├ <b>Romaji:</b> {title.get('romaji') or '—'}\n"
                f"├ <b>Japanese:</b> {title.get('native') or '—'}\n"
                f"├ <b>Type:</b> {manga.get('format') or '—'}\n"
                f"├ <b>Adult:</b> {'Yes' if manga.get('isAdult') else 'No'}\n"
                f"├ <b>Status:</b> {manga.get('status') or '—'}\n"
                f"├ <b>Chapters:</b> {manga.get('chapters') or '—'}\n"
                f"├ <b>Volumes:</b> {manga.get('volumes') or '—'}\n"
                f"├ <b>First Aired:</b> {manga.get('startDate') or '—'}\n"
                f"├ <b>Last Aired:</b> {manga.get('endDate') or '—'}\n"
                f"├ <b>Genres:</b> {', '.join(manga.get('genres', [])) or '—'}\n"
                f"├ <b>Trailer:</b> {trailer_url}\n\n"
                f"└ <b>『Description』</b>\n"
                f"{manga.get('description') or 'No description available.'}"
                "</blockquote>"
            )
    
            image = await self.client.utils.fetch_buffer(
                manga.get("coverImage")
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
                    "└ <i>Failed to fetch manga details.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            self.client.log.error(f"[ERROR] {e.__traceback__.tb_lineno}: {e}")