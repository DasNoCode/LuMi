from __future__ import annotations

from io import BytesIO
import time
from typing import Any, TYPE_CHECKING, Tuple

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
                "command": "guess",
                "category": "Game",
                "description": {
                    "content": "Guess the Pokémon in Who's That Pokémon.",
                    "usage": "<pokemon name>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        raw_text: str | None = context.get("text")

        if not raw_text:
            text: str = (
                "『<i>Invalid Input</i>』❌\n"
                "└ <i>Action</i>: Provide a Pokémon name"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        key: Tuple[str, int] = ("whos_that_pokemon", M.chat_id)
        game = self.client.interaction_store.get(key)

        if not game:
            text = (
                "『<i>No Active Game</i>』❌\n"
                "└ <i>Status</i>: No Pokémon quiz running"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        now: int = int(time.time())

        if now > game["expires_at"]:
            self.client.interaction_store.pop(key, None)

            text = (
                "『<i>Time Over</i>』⏰\n"
                "└ <i>Status</i>: The round has expired"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        guess: str = raw_text.lower().strip()
        answer: str = game["pokemon_name"].lower()

        if guess != answer:
            text = (
                "『<i>Wrong Guess</i>』❌\n"
                "└ <i>Action</i>: Try again before time runs out"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        self.client.interaction_store.pop(key, None)

        caption: str = (
            "『<i>Correct</i>』🎉\n"
            f"├ <i>Pokémon</i>: {game['pokemon_name'].title()}\n"
            f"└ <i>Guessed By</i>: {M.sender.mention}"
        )

        photo_bytes = await self.client.utils.generate_guess_pokemon(
            game["url"],
            answer,
            False,
        )

        img = BytesIO(photo_bytes)
        img.seek(0)

        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=img,
            caption=caption,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )