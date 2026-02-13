from __future__ import annotations

import traceback
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
                "command": "unmute",
                "category": "chat",
                "description": {
                    "content": "Unmute one or more users in the chat.",
                    "usage": "<@mention> or <reply>",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_restrict_members"],
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            users: list[Any] = []

            if M.reply_to_user:
                users.append(M.reply_to_user)
            elif M.mentions:
                users.extend(M.mentions)

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

            for user in users:
                member = await self.client.bot.get_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                already_unmuted: bool = (
                    member.can_send_messages is not False
                )

                if already_unmuted:
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "⚠️ <b>『Not Muted』</b>\n"
                            f"└ <i>{user.user_full_name or user.user_name} "
                            "is not muted.</i>"
                        ),
                        parse_mode="HTML",
                    )
                    continue

                await self.client.bot.restrict_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                    permissions=ChatPermissions.all_permissions(),
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "🔊 <b>『User Unmuted』</b>\n"
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
                    "└ <i>Something went wrong. Please try again later.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )