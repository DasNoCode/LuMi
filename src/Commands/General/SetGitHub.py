from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from telegram.constants import ParseMode

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "setgithub",
                "aliases": ["github"],
                "category": "general",
                "description": {
                    "content": "Set your GitHub username.",
                    "usage": "<username | remove>",
                },
                "OnlyPrivate": False,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        username: str = context.get("text", "").strip()

        if not username:
            return await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>GitHub Setup</i>』🐙\n"
                    f"└ <i>Usage</i>: {self.client.prefix}setgithub <username>"
                ),
                parse_mode=ParseMode.HTML,
                reply_to_message_id=M.message_id,
            )

        if username.lower() in {"remove", "none", "off"}:
            self.client.db.set_github(
                user_id=M.sender.user_id,
                github=None,
            )

            return await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>GitHub Updated</i>』✅\n"
                    "└ <i>Status</i>: Removed"
                ),
                parse_mode=ParseMode.HTML,
                reply_to_message_id=M.message_id,
            )

        username = username.replace("https://github.com/", "").strip("/")

        self.client.db.set_github(
            user_id=M.sender.user_id,
            github=username,
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=(
                "『<i>GitHub Updated</i>』✅\n"
                f"└ <i>Username</i>: "
                f'<a href="https://github.com/{username}">{username}</a>'
            ),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=M.message_id,
            disable_web_page_preview=True,
        )