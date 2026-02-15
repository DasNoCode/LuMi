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
                "command": "anime",
                "aliases": ["ani"],
                "category": "anime",
                "description": {
                    "content": "Search for anime details.",
                    "usage": "<anime_name>",
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
                    "└ <i>Please provide an anime name.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        try:
            animes: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/anime?search={query}"
            )
    
            if not animes:
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
                "🎬 <b>『Anime Search Results』</b>\n"
                f"├ <b>Query:</b> {query}\n"
                f"└ <b>Total Found:</b> {len(animes)}\n\n"
            )
    
            for i, anime in enumerate(animes, start=1):
                title: dict[str, str] = anime.get("title", {})
    
                text += (
                    f"#{i}\n"
                    f"├ <b>English:</b> {title.get('english') or '—'}\n"
                    f"├ <b>Romaji:</b> {title.get('romaji') or '—'}\n"
                    f"├ <b>Type:</b> {anime.get('format') or '—'}\n"
                    f"├ <b>Status:</b> {anime.get('status') or '—'}\n"
                    f"└ <b>More Info:</b> <code>{self.client.prefix}aid {anime.get('id')}</code>\n\n"
                )
    
            text += "</blockquote>"
    
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text.strip(),
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
                
    