from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand

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

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        raw_id: str = context.get("text", "").strip()

        if not raw_id.isdigit():
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>Invalid ID</i>』 ❌\n"
                    "└ You must provide a valid anime ID."
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        anime_id: int = int(raw_id)

        try:
            data: list[dict[str, Any]] = await self.client.utils.fetch(
                f"https://weeb-api.vercel.app/anime?search={anime_id}"
            )

            if not data:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "『<i>Not Found</i>』 🤔\n"
                        "└ No anime found for this ID."
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            anime: dict[str, Any] = data[0]
            title: dict[str, Any] = anime.get("title", {})

            name: str = (
                title.get("english")
                or title.get("romaji")
                or "Unknown"
            )

            trailer_id: str | None = anime.get("trailer", {}).get("id")
            trailer_url: str = (
                f"https://youtu.be/{trailer_id}"
                if trailer_id
                else "N/A"
            )

            genres: str = ", ".join(anime.get("genres", [])) or "—"

            text: str = (
                f"『<i>{name}</i>』 🎬\n"
                f"├ Romaji: {title.get('romaji') or '—'}\n"
                f"├ Japanese: {title.get('native') or '—'}\n"
                f"├ Type: {anime.get('format') or '—'}\n"
                f"├ Adult: {'Yes' if anime.get('isAdult') else 'No'}\n"
                f"├ Status: {anime.get('status') or '—'}\n"
                f"├ Episodes: {anime.get('episodes') or '—'}\n"
                f"├ Duration: {anime.get('duration') or '—'} min\n"
                f"├ First Aired: {anime.get('startDate') or '—'}\n"
                f"├ Last Aired: {anime.get('endDate') or '—'}\n"
                f"├ Genres: {genres}\n"
                f"├ Studios: {anime.get('studios') or '—'}\n"
                f"└ Trailer: {trailer_url}\n\n"
                f"『<i>Description</i>』 📖\n"
                f"{anime.get('description') or 'No description available.'}"
            )

            image = await self.client.utils.fetch_buffer(anime["imageUrl"])

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

