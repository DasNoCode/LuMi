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
                "command": "manga",
                "aliases": ["mang", "manhwa"],
                "category": "anime",
                "description": {
                    "content": "Search for manga details.",
                    "usage": "<manga_name>",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        query: str = context.get("text", "").strip()
    
        if not query:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Missing Query』</b>\n"
                    "└ <i>You forgot to provide a manga name.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        try:
            mangas: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/manga?search={query}"
            )
    
            if not mangas:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 <b>『No Results』</b>\n"
                        f"└ <i>No results found for \"{query}\".</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            text: str = (
                "<blockquote>"
                "📚 <b>『Manga Search Results』</b>\n"
                f"├ <b>Query:</b> {query}\n"
                f"└ <b>Total Found:</b> {len(mangas)}\n\n"
            )
    
            for i, manga in enumerate(mangas, start=1):
                title: dict[str, str] = manga.get("title", {})
                is_adult: bool = bool(manga.get("isAdult"))
                symbol: str = "🔞" if is_adult else "🌀"
    
                text += (
                    f"#{i}\n"
                    f"├ <b>English:</b> {title.get('english') or '—'}\n"
                    f"├ <b>Romaji:</b> {title.get('romaji') or '—'}\n"
                    f"├ <b>Status:</b> {manga.get('status') or '—'}\n"
                    f"├ <b>Adult:</b> {'Yes' if is_adult else 'No'} {symbol}\n"
                    f"└ <b>More Info:</b> <code>{self.client.prefix}mid {manga.get('id')}</code>\n\n"
                )
    
            text += "</blockquote>"
    
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text.strip(),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
    
        except Exception as e:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『Error』</b>\n"
                    "└ <i>Failed to fetch manga information.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            self.client.log.error(f"[ERROR] {e.__traceback__.tb_lineno}: {e}")