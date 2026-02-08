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
                "category": "chat",
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
            bots.append(f"├@{user.username}")

        if not bots:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="ℹ️ No bots found in this chat.",
                reply_to_message_id=M.message_id,
            )
            return

        text = (
            "<blockquote>"
            "<b>🤖 Bots in this chat</b>\n"
            + "\n".join(bots) +
            "\n</blockquote>"
        )

        await self.client.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )