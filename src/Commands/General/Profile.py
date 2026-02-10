from __future__ import annotations

import os
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
                "command": "profile",
                "category": "general",
                "description": {
                    "content": "Show user profile picture and details.",
                    "usage": "<reply> or <@mention>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        loading = await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="⌨",
            reply_to_message_id=M.message_id,
        )

        user = M.reply_to_user or (M.mentioned[0] if M.mentioned else None) or M.sender

        db_user = self.client.db.get_user_by_user_id(user.user_id)
        xp: int = db_user.xp if db_user else 0

        chat = await self.client.bot.get_chat(chat_id=user.user_id)
        user_bio: str = chat.bio or "N/A"

        avatar_url: str | None = await self.client.profile_photo_url(user_id=user.user_id)

        text = (
            "<blockquote>"
            f'<a href="{avatar_url}">&#8204;</a>'
            "👥 <b>User Information</b>\n"
            f"├ <b>Name:</b> {user.user_full_name}\n"
            f"├ <b>User ID:</b> <code>{user.user_id}</code>\n"
            f"├ <b>Username:</b> @{user.user_name or 'N/A'}\n"
            f"├ <b>XP:</b> {xp}\n"
            f"├ <b>Role:</b> {user.user_role}\n"
            f"└ <b>Bio:</b> {user_bio}"
            "</blockquote>"
        )

        await self.client.bot.delete_message(
            chat_id=M.chat_id,
            message_id=loading.message_id,
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )

            
