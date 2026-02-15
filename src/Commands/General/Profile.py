from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand

if TYPE_CHECKING:
    from telegram import User
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
        users: list[User] = []
        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentions:
            users.extend(M.mentions)
        else:
            users.append(M.sender)
        
        for user in users:
            db_user = self.client.db.get_user_by_user_id(user.user_id)
            xp: int = db_user.xp if db_user else 0
            github: str = db_user.github if db_user else "N/A"
    
            chat = await self.client.bot.get_chat(chat_id=user.user_id)
            user_bio: str = chat.bio or "N/A"
    
            avatar_url: str | None = await self.client.db.profile_to_url(
                user_id=user.user_id
            )
    
            text: str = (
                (f'<a href="{avatar_url}">&#8204;</a>' if avatar_url else "")
                + "『<i>User Information</i>』ℹ️\n"
                f"├ <i>Name</i>: {user.user_full_name}\n"
                f"├ <i>User ID</i>: <code>{user.user_id}</code>\n"
                f"├ <i>Username</i>: {user.mention}\n"
                + (
                    f"├ <i>GitHub</i>: "
                    f'<a href="https://github.com/{github}">{github}</a>\n'
                    if github else ""
                )
                + f"├ <i>XP</i>: {xp}\n"
                f"└ <i>Bio</i>: {user_bio}"
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