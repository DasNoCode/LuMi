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
                "command": "cid",
                "aliases": ["charid", "characterid"],
                "category": "anime",
                "description": {
                    "content": "Get anime character info by ID.",
                    "usage": "<character_id>",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        query: str = context.get("text", "").strip()
    
        if not query.isdigit():
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Invalid ID』</b>\n"
                    "└ <i>Please provide a valid character ID.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
    
        try:
            result: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/character?search={query}"
            )
    
            if not result:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 <b>『Not Found』</b>\n"
                        "└ <i>No character found for this ID.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return
    
            character: dict[str, Any] = result[0]
            name: dict[str, str] = character.get("name", {})
    
            gender: str = character.get("gender") or "Unknown"
            symbol: str = (
                "🚺" if gender == "Female"
                else "🚹" if gender == "Male"
                else "🚻"
            )
    
            description: str = character.get(
                "description",
                "No description available."
            )
    
            text: str = (
                "<blockquote>"
                "👤 <b>『Character Information』</b>\n"
                f"├ <b>Name:</b> {name.get('full') or '—'}\n"
                f"├ <b>Native:</b> {name.get('native') or '—'}\n"
                f"├ <b>ID:</b> <code>{character.get('id')}</code>\n"
                f"├ <b>Age:</b> {character.get('age') or 'Unknown'}\n"
                f"├ <b>Gender:</b> {gender} {symbol}\n"
                f"├ <b>AniList:</b> {character.get('siteUrl') or 'N/A'}\n\n"
                f"└ <b>『Description』</b>\n"
                f"{description}"
                "</blockquote>"
            )
    
            image = await self.client.utils.fetch_buffer(character["imageUrl"])
    
            await self.client.bot.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=text,
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
    