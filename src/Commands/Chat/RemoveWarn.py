from __future__ import annotations

from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from Models import User

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "removewarn",
                "aliases": ["unwarn"],
                "category": "moderation",
                "description": {
                    "content": "Remove warnings from a user.",
                    "usage": "<reply | @user> [all]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        text: str = context.get("text", "") or ""
        remove_all: bool = "all" in text.split()
        
        users: list[User] = []
        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentioned:
            users.extend(M.mentioned)
            
        for user in users:
            if user.user_id == self.client.bot.id:
                return
            if not user:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text="❌ Reply to a user or mention them to remove warns.",
                    reply_to_message_id=M.message_id,
                )
                return
    
            chat = self.client.db.get_group_by_chat_id(M.chat_id)
            warns: list[dict[str, Any]] = chat.warns or []
    
            entry = next(
                (w for w in warns if w.get("user_id") == user.user_id),
                None,
            )
    
            if not entry:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text="ℹ️ This user has no warnings.",
                    reply_to_message_id=M.message_id,
                )
                return
    
            if remove_all:
                warns.remove(entry)
                self.client.db._update_or_create_group(
                    M.chat_id,
                    {"warns": warns},
                )
    
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "<blockquote>"
                        f"├ <b>User:</b> {user.user_full_name}\n"
                        f"├ By: @{M.sender.user_name}\n"
                        "└ <b>All warnings removed</b> ✅"
                        "</blockquote>"
                    ),
                    parse_mode="HTML",
                    reply_to_message_id=M.message_id,
                )
                return
    
            entry["count"] = max(entry.get("count", 0) - 1, 0)
    
            if entry.get("reasons"):
                entry["reasons"].pop()
    
            if entry["count"] == 0:
                warns.remove(entry)
    
            self.client.db._update_or_create_group(
                M.chat_id,
                {"warns": warns},
            )
    
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "<blockquote>"
                    f"├ <b>User:</b> {user.user_full_name}\n"
                    f"├ By: @{M.sender.user_name}\n"
                    f"└ <b>Warnings:</b> {entry.get('count', 0)}/3"
                    "</blockquote>"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )