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
        query = " ".join(context.get("args", [])).strip() if context else None

        if not query or not query.isdigit():
            return await self.client.send_message(
                M.chat_id,
                "❌ Looks like you forgot to type a valid character ID.",
                reply_to_message_id=M.message_id,
            )

        try:
            url = f"https://weeb-api.vercel.app/character?search={query}"
            result = self.client.utils.fetch(url)

            if not result:
                return await self.client.send_message(
                    M.chat_id,
                    "🤔 Hmm... I couldn't find anything matching that character ID.",
                    reply_to_message_id=M.message_id,
                )

            character = result[0]
            gender = character.get("gender", "Unknown")
            symbol = (
                "🚺"
                if gender == "Female"
                else "🚹" if gender == "Male" else "🚻"
            )

            msg = (
                f"👤 Name: {character['name']['full']}\n"
                f"💠 Native: {character['name']['native']}\n"
                f"🆔 ID: {character['id']}\n"
                f"🗓 Age: {character.get('age', 'Unknown')}\n"
                f"🔗 Gender: {gender} {symbol}\n"
                f"🔗 AniList: {character.get('siteUrl', 'N/A')}\n\n"
                f"📝 Description:\n{character.get('description', 'No description available.')}"
            )

            image = self.client.utils.fetch_buffer(character["imageUrl"])
            await self.client.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=msg,
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch character info. Please try again later.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [CharacterID] {e}")
