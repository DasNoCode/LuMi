from __future__ import annotations

from typing import Any, TYPE_CHECKING
from telegram import ChatPermissions

from Libs import BaseCommand


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "unlock",
                "category": "chat",
                "description": {
                    "content": "Unlock the chat (restore previous permissions).",
                    "usage": "",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
                "admin_permissions": [
                    "can_restrict_members",
                    "can_change_info",
                ],
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        group = self.client.db.get_group_by_chat_id(M.chat_id)

        stored_perms = getattr(group, "permissions", None)

        if not stored_perms:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "⚠️ <b>『No Stored Permissions』</b>\n"
                    "└ <i>No previous permissions found to restore.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        await self.client.bot.set_chat_permissions(
            chat_id=M.chat_id,
            permissions=ChatPermissions(**stored_perms),
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=(
                "🔓 <b>『Chat Unlocked』</b>\n"
                f"└ <b>By:</b> "
                f"{M.sender.user_name or M.sender.user_full_name}"
            ),
            reply_to_message_id=M.message_id,
            parse_mode="HTML",
        )