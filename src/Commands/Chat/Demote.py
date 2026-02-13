from __future__ import annotations
import traceback
from Libs import BaseCommand
from typing import Any, TYPE_CHECKING


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
                "command": "demote",
                "category": "chat",
                "description": {
                    "content": "Demote one or more admins to regular users.",
                    "usage": "<@mention> or <reply>",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": ["can_promote_members"],
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

                if user.user_id == M.sender.user_id:
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "❌ <b>『Action Denied』</b>\n"
                            "└ <i>You cannot demote yourself.</i>"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                member = await self.client.bot.get_chat_member(
                    M.chat_id,
                    user.user_id,
                )

                if member.status == "creator":
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "❌ <b>『Action Denied』</b>\n"
                            f"└ <i>Cannot demote group owner: "
                            f"{user.user_full_name}</i>"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                if user.user_id == M.bot_user_id:
                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=(
                            "❌ <b>『Action Denied』</b>\n"
                            "└ <i>I cannot demote myself.</i>"
                        ),
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                await self.client.bot.promote_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                    can_change_info=False,
                    can_post_messages=False,
                    can_edit_messages=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    is_anonymous=False,
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "✅ <b>『User Demoted』</b>\n"
                        f"├ <b>User:</b> "
                        f"{user.user_full_name or user.user_name}\n"
                        f"└ <b>ID:</b> <code>{user.user_id}</code>"
                    ),
                    reply_to_message_id=M.message_id,
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