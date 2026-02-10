from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "guesspoke",
                "aliases": ["whosthatpokemon"],
                "category": "game",
                "description": {
                    "content": "Enable or disable Who's That Pokémon in this chat.",
                    "usage": "on | off",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        if M.is_callback:
            state: str | None = context.get("flags", {}).get("state")
            if state not in {"on", "off"}:
                return

            enabled: bool = state == "on"

            self.client.db._update_or_create_group(
                M.chat_id,
                {"whos_that_pokemon": enabled},
            )
            self.client.start_whos_that_pokemon_scheduler()

            await self.client.bot.edit_message_text(
                chat_id=M.chat_id,
                message_id=M.message_id,
                text=(
                    "<blockquote>"
                    "🎮 <b>Whos That Pokémon</b>\n"
                    f"└ <b>Status:</b> {'Enabled ✅' if enabled else 'Disabled ❌'}"
                    "</blockquote>"
                ),
                parse_mode="HTML",
            )
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Enable",
                        callback_data="cmd:guesspoke state:on",
                    ),
                    InlineKeyboardButton(
                        "❌ Disable",
                        callback_data="cmd:guesspoke state:off",
                    ),
                ]
            ]
        )

        chat = self.client.db.get_group_by_chat_id(M.chat_id)
        enabled: bool = getattr(chat, "pokemon_enabled", True)

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=(
                "<blockquote>"
                "🎮 <b>Who's That Pokémon</b>\n"
                f"└ <b>Status:</b> {'Enabled ✅' if enabled else 'Disabled ❌'}"
                "</blockquote>"
            ),
            reply_markup=keyboard,
            reply_to_message_id=M.message_id,
            parse_mode="HTML",
        )