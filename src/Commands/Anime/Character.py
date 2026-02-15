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
                "command": "character",
                "aliases": ["char", "csearch"],
                "category": "anime",
                "description": {
                    "content": "Search for anime character details.",
                    "usage": "<character_name>",
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
                    "└ <i>Please provide a character name.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        try:
            characters: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/character?search={query}"
            )
    
            if not characters:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 <b>『No Results』</b>\n"
                        f"└ <i>No characters found for \"{query}\".</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            text: str = (
                "<blockquote>"
                "👤 <b>『Character Search Results』</b>\n"
                f"├ <b>Query:</b> {query}\n"
                f"└ <b>Total Found:</b> {len(characters)}\n\n"
            )
    
            for i, char in enumerate(characters, start=1):
                name: dict[str, str] = char.get("name", {})
                gender: str = char.get("gender") or "Unknown"
    
                symbol: str = (
                    "🚺" if gender == "Female"
                    else "🚹" if gender == "Male"
                    else "🚻"
                )
    
                text += (
                    f"#{i}\n"
                    f"├ <b>Full Name:</b> {name.get('full') or '—'}\n"
                    f"├ <b>Native Name:</b> {name.get('native') or '—'}\n"
                    f"├ <b>Gender:</b> {gender} {symbol}\n"
                    f"└ <b>More Info:</b> <code>{self.client.prefix}cid {char.get('id')}</code>\n\n"
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
                
