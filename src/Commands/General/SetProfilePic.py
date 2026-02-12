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
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text = (
                    "❌ <b>『Invalid Action』</b>\n"
                    "└ <i>Reply to a photo or send a photo with caption to set profile picture.</i>"
                ),
                reply_to_message_id=M.message_id,
            )
            return

        file_path: str = await self.client.download_media(photo_file_id)
        path: Path = Path(file_path)

        try:
            avatar_url: str = self.client.utils.img_to_url(str(path))
            print(avatar_url)

            self.client.db.set_user_profile_photo(
                M.sender.user_id,
                avatar_url,
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text = (
                    "👤 <b>『Profile Update』</b>\n"
                    f"├ <b>User:</b> {M.sender.mention}\n"
                    "└ <b>Profile photo updated successfully</b> ✅"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )

        finally:
            try:
                os.remove(path)
            except Exception:
                pass