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
                "command": "aid",
                "aliases": ["animeid"],
                "category": "anime",
                "description": {
                    "content": "Get detailed info of anime by ID.",
                    "usage": "<anime_id>",
                },
                "xp": 1,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        # ⛔ Validate input
        if not context or not context[0].isdigit():
            return await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ Looks like you forgot to type the anime ID.",
                reply_to_message_id=M.message_id,
            )

        anime_id = context[0]

        try:
            # 🌐 Fetch anime data
            data = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/anime?search={anime_id}"
            )

            if not data:
                return await self.client.send_message(
                    chat_id=M.chat_id,
                    text="🤔 Hmm... I couldn't find anything matching your search.",
                    reply_to_message_id=M.message_id,
                )

            anime = data[0]

            # 🧾 Build response message
            msg = (
                f"🎬 *{anime['title']['english']}* *|* {anime['title']['romaji']}\n"
                f"💠 *Japanese Name:* {anime['title']['native']}\n"
                f"📀 *Type:* {anime['format']}\n"
                f"🔖 *Is Adult:* {'Yes' if anime['isAdult'] else 'No'}\n"
                f"📡 *Status:* {anime['status']}\n"
                f"🎞 *Episodes:* {anime['episodes']}\n"
                f"🕒 *Duration:* {anime['duration']} min per episode\n"
                f"🗓 *First Aired:* {anime['startDate']}\n"
                f"📅 *Last Aired:* {anime['endDate']}\n"
                f"🎨 *Genres:* {', '.join(anime['genres'])}\n"
                f"🏢 *Studios:* {anime['studios']}\n"
                f"🎥 *Trailer:* https://youtu.be/{anime.get('trailer', {}).get('id', 'null')}\n\n"
                f"📖 *Description:*\n{anime['description']}"
            )

            # 🖼️ Send photo with caption
            image = await self.client.utils.fetch_buffer(anime["imageUrl"])
            await self.client.send_photo(
                chat_id=M.chat_id,
                photo=image,
                caption=msg,
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="⚠️ An error occurred while fetching anime data.",
                reply_to_message_id=M.message_id,
            )
            self.client.log.error(f"[ERROR] [AnimeID] {e}")
