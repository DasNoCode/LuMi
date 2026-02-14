from __future__ import annotations

from typing import Any, TYPE_CHECKING

from telegram import ChatAdministratorRights
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
                "command": "demote",
                "category": "Chat",
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
                text: str = (
                    "『<i>Invalid Usage</i>』❗\n"
                    "└ <i>Action</i>: Mention or reply to a user"
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=text,
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            for user in users:

                if user.user_id == M.sender.user_id:
                    text = (
                        "『<i>Action Denied</i>』❌\n"
                        "└ <i>Reason</i>: You cannot demote yourself"
                    )

                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=text,
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                member = await self.client.bot.get_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                )

                if member.status == "creator":
                    text = (
                        "『<i>Action Denied</i>』❌\n"
                        f"└ <i>Reason</i>: Cannot demote group owner"
                    )

                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=text,
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                if user.user_id == self.client.bot_user_id:
                    text = (
                        "『<i>Action Denied</i>』❌\n"
                        "└ <i>Reason</i>: I cannot demote myself"
                    )

                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=text,
                        reply_to_message_id=M.message_id,
                        parse_mode="HTML",
                    )
                    continue

                await self.client.bot.promote_chat_member(
                    chat_id=M.chat_id,
                    user_id=user.user_id,
                    **ChatAdministratorRights.no_rights().to_dict(),
                )

                text = (
                    "『<i>User Demoted</i>』📉\n"
                    f"├ <i>User</i>: {user.mention}\n"
                    "└ <i>Status</i>: Regular Member"
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=text,
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )

        except Exception as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )

            text = (
                "『<i>Error</i>』⚠️\n"
                "└ <i>Action</i>: Please try again later"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )