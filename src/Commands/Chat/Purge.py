from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from telegram.error import BadRequest


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "purge",
                "aliases": ["clear", "clean"],
                "category": "chat",
                "description": {
                    "content": "Delete recent messages from the chat.",
                    "usage": "[count]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_delete_messages"],
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        count: int = 10

        args = context.get("args", [])
        if args and args[0].isdigit():
            count = min(int(args[0]), 1000)

        start_id: int = M.message_id
        message_ids: list[int] = list(
            range(start_id, max(start_id - count, 0), -1)
        )

        chunk_size: int = 100

        for i in range(0, len(message_ids), chunk_size):
            chunk = message_ids[i : i + chunk_size]
            try:
                await self.client.bot.delete_messages(
                    chat_id=M.chat_id,
                    message_ids=chunk,
                )
            except BadRequest:
                pass

        try:
            confirm = await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "🧹 <b>『Chat Purged』</b>\n"
                    f"└ <b>Messages Cleared:</b> {len(message_ids)}"
                ),
                parse_mode="HTML",
            )

            await self.client.bot.delete_message(
                chat_id=M.chat_id,
                message_id=confirm.message_id,
            )
        except Exception:
            pass