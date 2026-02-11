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
                "command": "ban",
                "category": "chat",
                "description": {
                    "content": "Ban one or more users from the chat.",
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
            elif M.mentioned:
                users.extend(M.mentioned)

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

            raw_text: str = context.get("text", "").strip()
            reason: str = " ".join(
                word for word in raw_text.split()
                if not word.startswith("@")
            )

            for user in users:
                member = await self.client.bot.get_chat_member(
                    M.chat_id,
                    user.user_id,
                )

                if member.status == "creator":
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "❌ <b>『Action Denied』</b>\n"
                            f"└ <i>Cannot ban group owner: "
                            f"{user.user_full_name or user.user_name}</i>"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                if user.user_id == M.bot_userid:
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "❌ <b>『Action Denied』</b>\n"
                            "└ <i>I cannot ban myself.</i>"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                self.client.db.manage_banned_user(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                    by_user_id=M.sender.user_id,
                    ban=True,
                    reason=reason,
                )

                await self.client.bot.ban_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "✅ <b>『User Banned』</b>\n"
                        f"├ <b>User:</b> "
                        f"{user.user_full_name or user.user_name}\n"
                        f"├ <b>ID:</b> <code>{user.user_id}</code>\n"
                        + (
                            f"└ <b>Reason:</b> {reason}"
                            if reason
                            else "└ <i>No reason provided.</i>"
                        )
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