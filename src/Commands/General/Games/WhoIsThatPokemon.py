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
                "category": "game",
                "description": {
                    "content": "Guess the Pokémon in Who's That Pokémon.",
                    "usage": "<pokemon name>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        text: str = context.get("text", None)
        if not text:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text = (
                    "❌ <b>『Invalid Input』</b>\n"
                    "└ <i>Please provide a Pokémon name.</i>"
                ),
                reply_to_message_id=M.message_id,
            )
            return

        key: Tuple[int, int] = ("whos_that_pokemon", M.chat_id)
        game = self.client.interaction_store.get(key)
        if not game:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ No active Pokémon quiz right now.",
                reply_to_message_id=M.message_id,
            )
            return

        now: int = int(time.time())

        if now > game["expires_at"]:
            self.client.interaction_store.pop(key, None)
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="⏰ Oops! You missed it. Time is over.",
                reply_to_message_id=M.message_id,
            )
            return

        guess: str = (text).lower()
        answer: str = game["pokemon_name"].lower()
        print(guess,answer, guess == answer)
        if guess != answer:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text= (
                    "❌ <b>『Wrong Guess』</b>\n"
                    "└ <i>Try again before time runs out.</i>"
                ),
                reply_to_message_id=M.message_id,
            )
            return

        self.client.interaction_store.pop(key, None)

        text = (
            f"🎉 <b>『Correct』</b>\n"
            f"├ Pokémon: <b>{game['pokemon_name'].title()}</b>\n"
            f"└ Guessed by: <b>{M.sender.mention}</b>"
        )
        print(game["url"])
        photo = await self.client.utils.generate_guess_pokemon(game["url"], answer, False)
        img = BytesIO(photo)
        img.seek(0)
        await self.client.bot.send_photo(
            chat_id=M.chat_id,
            photo=img,
            caption=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )