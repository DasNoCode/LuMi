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
        elif M.mentions:
            users.extend(M.mentions)

        if not users:
            text: str = (
                "『<i>Invalid Usage</i>』❗\n"
                "└ <i>Action</i>: Reply or mention a user to warn"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        for user in users:
            if user.is_bot or user.user_id == self.client.bot.id:
                continue

            raw_text: str = context.get("text", "") or ""
            reason: str = " ".join(
                word for word in raw_text.split()
                if not word.startswith("@")
            )

            count: int = self.client.db.add_warn(
                chat_id=M.chat_id,
                user_full_name=user.user_full_name,
                user_id=user.user_id,
                reason=reason,
                by_user_id=M.sender.user_id,
            )

            if count >= 3:
                await self.client.kick_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                text: str = (
                    "『<i>User Kicked</i>』🚫\n"
                    f"├ <i>User</i>: {user.mention}\n"
                    f"├ <i>By</i>: {M.sender.mention}\n"
                    "├ <i>Warns</i>: 3/3\n"
                    f"└ <i>Reason</i>: {reason or 'No reason provided'}"
                )
            else:
                text = (
                    "『<i>User Warned</i>』📍\n"
                    f"├ <i>User</i>: {user.mention}\n"
                    f"├ <i>By</i>: {M.sender.mention}\n"
                    f"├ <i>Warns</i>: {count}/3\n"
                    f"└ <i>Reason</i>: {reason or 'No reason provided'}"
                )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )