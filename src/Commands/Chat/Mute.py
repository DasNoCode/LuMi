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
        users: list[Any] = []

        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentioned:
            users.extend(M.mentioned)

        if not users:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❗ <b>『Invalid Usage』</b>\n"
                    "└ <i>Reply to a user or mention at least one user.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return
        
        flags: dict[str, Any] = context.get("flags", {})
        time_value = flags.get("time")

        if time_value is not None:
            try:
                minutes: int = int(time_value)
                until_date = timedelta(minutes=minutes)
                label: str = f"{minutes} minutes"
                explicit: bool = True
            except (TypeError, ValueError):
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❌ <b>『Invalid Time』</b>\n"
                        "└ <i>Use time:&lt;minutes&gt;</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
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
            if member.ADMINISTRATOR:
                return
            
            already_muted: bool = member.can_send_messages is False

            if already_muted and not explicit:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "⚠️ <b>『Already Muted』</b>\n"
                        f"└ <i>{user.user_full_name or user.user_name} "
                        "is already muted.</i>"
                    ),
                    parse_mode="HTML",
                )
                continue

            await self.client.bot.restrict_chat_member(
                chat_id=M.chat_id,
                user_id=user.user_id,
                permissions=ChatPermissions.no_permissions(),
                until_date=until_date,
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "🔇 <b>『User Muted』</b>\n"
                    f"├ <b>User:</b> "
                    f"{user.user_full_name or user.user_name}\n"
                    f"└ <b>Duration:</b> {label}"
                ),
                parse_mode="HTML",
            )