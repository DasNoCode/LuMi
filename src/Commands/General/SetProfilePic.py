from __future__ import annotations

import os
from pathlib import Path
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
                "command": "setpfp",
                "aliases": ["setprofile", "setavatar"],
                "category": "general",
                "description": {
                    "content": "Update your profile photo in the database.",
                    "usage": "<reply to photo> or <send photo with caption>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        photo_file_id: str | None = None

        if M.reply_to_message and M.reply_to_message.photo:
            photo_file_id = M.reply_to_message.photo[-1].file_id

        elif M.msg_type == "photo":
            photo_file_id = M.file_id

        if not photo_file_id:
            text: str = (
                "『<i>Invalid Action</i>』❌\n"
                "└ <i>Usage</i>: Reply to a photo or send one with caption"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        file_path: str = await self.client.download_media(photo_file_id)
        path: Path = Path(file_path)

        try:
            avatar_url: str = self.client.utils.img_to_url(str(path))

            self.client.db.set_user_profile_photo(
                M.sender.user_id,
                avatar_url,
            )

            text: str = (
                "『<i>Profile Updated</i>』👤\n"
                f"├ <i>User</i>: {M.sender.mention}\n"
                "└ <i>Status</i>: Profile photo updated successfully ✅"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )

        finally:
            try:
                os.remove(path)
            except Exception:
                pass