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
        query = " ".join(context.get("args", [])).strip() if context else None

        if not query:
            return await self.client.send_message(
                M.chat_id,
                "❌ Looks like you forgot to type the manga name.",
                reply_to_message_id=M.message_id,
            )

        try:
            url = f"https://weeb-api.vercel.app/manga?search={query}"
            mangas = self.client.utils.fetch(url)

            if not mangas:
                return await self.client.send_message(
                    M.chat_id,
                    "🤔 Hmm... I couldn't find anything matching your search. Maybe try a different name?",
                    reply_to_message_id=M.message_id,
                )

            msg = f"📚 Manga Search Results 📚\n\nHere’s what I found for {query} ⚡︎\n\n"

            for i, manga in enumerate(mangas):
                symbol = "🔞" if manga.get("isAdult") else "🌀"
                msg += (
                    f"#{i + 1}\n"
                    f"📖 English name: {manga['title']['english']}\n"
                    f"🌐 Alternative Name: {manga['title']['romaji']}\n"
                    f"📌 Status: {manga['status']}\n"
                    f"⚠️ Is Adult: {manga['isAdult']} {symbol}\n"
                    f"🔎 More Info: {self.client.config.prefix}mid {manga['id']}\n\n"
                )

            await self.client.send_message(
                M.chat_id,
                msg.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch manga info. Please try again later.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [MangaSearch] {e}")
