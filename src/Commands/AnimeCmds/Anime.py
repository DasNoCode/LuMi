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

        query = " ".join(context.get("args", [])).strip() if context else None

        if not query:
            return await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ Looks like you forgot to type the anime name.",
                reply_to_message_id=M.message_id,
            )

        try:
            animes = self.client.utils.fetch(
                f"https://weeb-api.vercel.app/anime?search={query}"
            )

            if not animes:
                return await self.client.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🤔 Hmm... I couldn't find anything matching your search. "
                        "Maybe try a different name?"
                    ),
                    reply_to_message_id=M.message_id,
                )

            msg = (
                f"🎬 Anime Search Results\n\n"
                f"Here’s what I found for {query} ⚡︎\n\n"
            )

            for i, anime in enumerate(animes):
                msg += (
                    f"#{i+1}\n"
                    f"🎬 English name: {anime['title']['english']}\n"
                    f"💠 Alternative name: {anime['title']['romaji']}\n"
                    f"📀 Type: {anime['format']}\n"
                    f"📡 Status: {anime['status']}\n"
                    f"🔎 More Info: {self.client.prefix}aid {anime['id']}\n\n"
                )

            await self.client.send_message(
                chat_id=M.chat_id,
                text=msg.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="⚠️ Something went wrong while fetching the anime data.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [AnimeSearch] {e}")
