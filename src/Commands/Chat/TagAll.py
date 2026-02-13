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
                "command": "tagall",
                "aliases": ["all"],
                "category": "chat",
                "description": {
                    "content": "Silently tag all chat members. Limit 190 per batch.",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        members = self.client.pyrogram_Client.get_chat_members(M.chat_id)

        user_ids: list[int] = [
            m.user.id
            async for m in members
            if not m.user.is_bot
        ]

        if not user_ids:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『No Users Found』</b>\n"
                    "└ <i>No eligible users to tag.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode=ParseMode.HTML,
            )
            return

        for i in range(0, len(user_ids), 190):
            chunk = user_ids[i : i + 190]

            mentions: str = "".join(
                f'<a href="tg://user?id={uid}">\u200c</a>'
                for uid in chunk
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "📢 <b>『Tag All』</b>\n"
                    f"└ @everyone {mentions}"
                ),
                parse_mode=ParseMode.HTML,
            )