from __future__ import annotations

from typing import Any, TYPE_CHECKING

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
                "command": "profile",
                "category": "general",
                "description": {
                    "content": "Show user profile picture and details.",
                    "usage": "<reply> or <@mention>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        user = (
            M.reply_to_user
            or (M.mentioned[0] if M.mentioned else None)
            or M.sender
        )
        
        db_user = self.client.db.get_user_by_user_id(user.user_id)
        xp: int = db_user.xp
        photo: str = await self.client.download_media(user.user_profile_id)
        text = (
            "<blockquote>"
            f"<b>Name:</b> {user.user_full_name}\n"
            f"<b>Username:</b> @{user.user_name or 'N/A'}\n"
            f"<b>User ID:</b> <code>{user.user_id}</code>\n"
            f"<b>XP:</b> {xp}"
            "</blockquote>"
        )
        
        if photo:
            await self.client.send_photo(
                chat_id=M.chat_id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
        else:
            await self.client.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
