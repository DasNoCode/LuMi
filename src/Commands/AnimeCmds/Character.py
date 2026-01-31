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
        query = " ".join(context.get("args", [])).strip() if context else None

        if not query:
            return await self.client.send_message(
                M.chat_id,
                "❌ Looks like you forgot to type the character name.",
                reply_to_message_id=M.message_id,
            )

        try:
            url = f"https://weeb-api.vercel.app/character?search={query}"
            characters = self.client.utils.fetch(url)

            if not characters:
                return await self.client.send_message(
                    M.chat_id,
                    "🤔 Hmm... I couldn't find any character matching your search. Maybe double-check the name?",
                    reply_to_message_id=M.message_id,
                )

            msg = (
                f"👤 Character Search Results 👤\n\n"
                f"Here’s what I found for {query} ⚡︎\n\n"
            )

            for i, char in enumerate(characters):
                gender = char.get("gender", "Unknown")
                symbol = (
                    "🚺"
                    if gender == "Female"
                    else "🚹" if gender == "Male" else "🚻"
                )

                msg += (
                    f"#{i+1}\n"
                    f"🌀 Full name: {char['name']['full']}\n"
                    f"💠 Native name: {char['name']['native']}\n"
                    f"🔗 Gender: {gender} {symbol}\n"
                    f"🔎 More Info: {self.client.prefix}cid {char['id']}\n\n"
                )

            await self.client.send_message(
                M.chat_id,
                msg.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch character data. Please try again later.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [CharacterSearch] {e}")
