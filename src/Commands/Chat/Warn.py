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
                "command": "warn",
                "category": "chat",
                "description": {
                    "content": "Warn a user. Kicks at 3 warns.",
                    "usage": "<reply or mention> [reason]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        users: list[User] = []
        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentioned:
            users.extend(M.mentioned)

        if not users:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ Reply to a user or mention them to warn.",
                reply_to_message_id=M.message_id,
            )
            return

        for user in users:
            if user.user_id == self.client.bot.id:
                return

            text: str = context.get("text", None)
            reason = " ".join(word for word in text.split() if not word.startswith("@"))

            count: int = self.client.db.add_warn(
                chat_id=M.chat_id,
                user_full_name= user.user_full_name,
                user_id=user.user_id,
                reason=reason,
                by_user_id=M.sender.user_id
            )

            if count >= 3:
                await self.client.kick_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                text = (
                    "<blockquote>"
                    "<b>🚫 User Kicked</b>\n"
                    f"├ User: {user.user_full_name}\n"
                    f"├ By: @{M.sender.user_name}\n"
                    "├ Warns: 3/3\n"
                    f"└ Reason: {reason or 'No reason provided'}"
                    "</blockquote>"
                )
            else:
                text = (
                    "<blockquote>"
                    "<b>⚠️ User Warned</b>\n"
                    f"├ User: {user.user_full_name}\n"
                    f"├ By: @{M.sender.user_name}\n"
                    f"├ Warns: {count}/3\n"
                    f"└ Reason: {reason or 'No reason provided'}"
                    "</blockquote>"
                )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
