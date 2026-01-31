from __future__ import annotations

import random
from datetime import timedelta
from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from telegram import ChatPermissions

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "mute",
                "category": "chat",
                "description": {
                    "content": "Mute one or more users in the chat.",
                    "usage": "<@mention> or <reply> [time:<minutes>]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_restrict_members"],
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        users = []

        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentioned:
            users.extend(M.mentioned)

        if not users:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="❗ Reply to a user or mention at least one user to mute.",
                reply_to_message_id=M.message_id,
            )
            return

        flags = context.get("flags", {})
        time_value = flags.get("time")

        if time_value is not None:
            try:
                minutes = int(time_value)
                until_date = timedelta(minutes=minutes)
                label = f"{minutes} minutes"
                explicit = True
            except (TypeError, ValueError):
                await self.client.send_message(
                    chat_id=M.chat_id,
                    text="❌ Invalid time value. Use time:<minutes>",
                    reply_to_message_id=M.message_id,
                )
                return
        else:
            minutes = random.randint(5, 55)
            until_date = timedelta(minutes=minutes)
            label = f"{minutes} minutes"
            explicit = False

        for user in users:
            member = await self.client.bot.get_chat_member(
                chat_id=M.chat_id,
                user_id=user.user_id,
            )

            already_muted = (
                member.can_send_messages is False
            )

            if already_muted and not explicit:
                await self.client.send_message(
                    chat_id=M.chat_id,
                    text=f"⚠️ {user.user_full_name or user.user_name} is already muted.",
                )
                continue

            await self.client.bot.restrict_chat_member(
                chat_id=M.chat_id,
                user_id=user.user_id,
                permissions=ChatPermissions.no_permissions(),
                until_date=until_date,
            )

            await self.client.send_message(
                chat_id=M.chat_id,
                text=f"🔇 {user.user_full_name or user.user_name} muted for {label}.",
            )
