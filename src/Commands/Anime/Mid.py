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
        if not context or not str(context[0]).isdigit():
            return await self.client.send_message(
                M.chat_id,
                "❌ Looks like you forgot to type the manga ID.",
                reply_to_message_id=M.message_id,
            )

        manga_id = context[0]

        try:
            url = f"https://weeb-api.vercel.app/manga?search={manga_id}"
            results = self.client.utils.fetch(url)

            if not results:
                return await self.client.send_message(
                    M.chat_id,
                    "🤔 Hmm... I couldn't find anything matching that manga ID.",
                    reply_to_message_id=M.message_id,
                )

            manga = results[0]
            title = manga["title"]

            message = (
                f"📚 {title['english']} | {title['romaji']}\n"
                f"🈶 Japanese: {title['native']}\n"
                f"📦 Type: {manga['format']}\n"
                f"⚠️ Is Adult: {'Yes' if manga['isAdult'] else 'No'}\n"
                f"📌 Status: {manga['status']}\n"
                f"📖 Chapters: {manga['chapters']}\n"
                f"📦 Volumes: {manga['volumes']}\n"
                f"⏳ First Aired: {manga['startDate']}\n"
                f"🕰️ Last Aired: {manga['endDate']}\n"
                f"🎭 Genres: {', '.join(manga['genres'])}\n"
                f"🎬 Trailer: https://youtu.be/{manga['trailer']['id'] if manga.get('trailer') else 'null'}\n\n"
                f"📄 Description:\n_{manga['description']}_"
            )

            image = self.client.utils.fetch_buffer(manga["coverImage"])
            await self.client.send_image(
                M.chat_id,
                image,
                message.strip(),
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                M.chat_id,
                "⚠️ Failed to fetch manga info. Please try again later.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [MangaDetail] {e}")
