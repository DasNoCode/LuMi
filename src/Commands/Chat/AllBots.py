from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from pyrogram import enums


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "all_bots",
                "aliases": ["bots"],
                "category": "Chat",
                "description": {
                    "content": "List all bots present in this chat.",
                },
                "OnlyChat": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        bots: list[str] = []

        async for member in self.client.pyrogram_Client.get_chat_members(
            chat_id=M.chat_id,
            filter=enums.ChatMembersFilter.BOTS,
        ):
            user = member.user
            username: str = (
                f"@{user.username}"
                if user.username
                else user.first_name
            )
            bots.append(username)

        if not bots:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "ℹ️ <b>『No Bots Found』</b>\n"
                    "└ <i>There are no bots in this chat.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        lines: list[str] = []
        for i, bot in enumerate(bots):
            prefix: str = "└" if i == len(bots) - 1 else "├"
            lines.append(f"{prefix} {bot}")

        text: str = (
            "<blockquote>"
            "🤖 <b>『Bots in This Chat』</b>\n"
            + "\n".join(lines) +
            "\n</blockquote>"
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )