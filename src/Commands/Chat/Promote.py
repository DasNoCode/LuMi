from __future__ import annotations

from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from telegram.error import BadRequest


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):

    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "promote",
                "category": "Chat",
                "description": {
                    "content": "Promote a user with limited or full admin rights.",
                    "usage": "<reply | @user> [full]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:

        text: str = context.get("text", "") or ""
        is_full: bool = "full" in text.lower()

        target = (
            M.reply_to_user
            or (M.mentions[0] if M.mentions else None)
        )

        if not target:
            text: str = (
                "『<i>Invalid Usage</i>』❌\n"
                "└ <i>Action</i>: Reply or mention a user"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
            return

        member = await self.client.bot.get_chat_member(
            chat_id=M.chat_id,
            user_id=target.user_id,
        )

        if member.status == "creator":
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Action Denied』</b>\n"
                    f"└ <i>Cannot promote group owner: "
                    f"{target.mention}</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        if target.user_id == self.client.bot_user_id:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『Action Denied』</b>\n"
                    "└ <i>I cannot promote myself.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        try:

            if is_full:
                await self.client.bot.promote_chat_member(
                    chat_id=M.chat_id,
                    user_id=target.user_id,
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    is_anonymous=False,
                )
                mode_text = "Full Admin Rights"

            else:
                await self.client.bot.promote_chat_member(
                    chat_id=M.chat_id,
                    user_id=target.user_id,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    is_anonymous=False,
                )
                mode_text = "Limited Admin Rights"

        except BadRequest as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )
            return

        text = (
            "『<i>User Promoted</i>』📈\n"
            f"├ <i>User</i>: {target.mention}\n"
            f"└ <i>Mode</i>: {mode_text}"
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )