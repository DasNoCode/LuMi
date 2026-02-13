from __future__ import annotations

import traceback
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
                "command": "unban",
                "category": "chat",
                "description": {
                    "content": "Unban one or more users from the chat.",
                    "usage": "<@mention> or <reply>",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_restrict_members"],
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            users: list[User] = []

            if M.reply_to_user:
                users.append(M.reply_to_user)
            elif M.mentions:
                users.extend(M.mentions)

            if not users:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "❗ <b>『Invalid Usage』</b>\n"
                        "└ <i>Mention at least one user or reply to a message.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            for user in users:
                member = await self.client.bot.get_chat_member(
                    M.chat_id,
                    user.user_id,
                )

                if member.status == "creator":
                    continue

                if user.user_id == M.bot_userid:
                    continue

                await self.client.bot.unban_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                self.client.db.manage_banned_user(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                    ban=False,
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "♻️ <b>『User Unbanned』</b>\n"
                        f"├ <b>User:</b> "
                        f"{user.user_full_name or user.user_name}\n"
                        f"└ <b>ID:</b> <code>{user.user_id}</code>"
                    ),
                    parse_mode="HTML",
                )

        except Exception as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『Error』</b>\n"
                    "└ <i>Failed to unban user(s).</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )