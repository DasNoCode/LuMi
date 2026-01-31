from __future__ import annotations

from datetime import timedelta
from typing import Any, TYPE_CHECKING

from telegram import ChatPermissions

from Libs import BaseCommand
import time

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "jobtest",
                "category": "general",
                "description": {"content": "Say hello to the bot"},
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        photos = await self.client.bot.get_user_profile_photos(M.sender.user_id)
        print(photos.total_count)
        profile_path: str = await self.client.download_media(photos.photos[0][-1].file_id)
        await self.client.send_photo(chat_id=M.chat_id, photo=profile_path
)














#
#        self.client.job_queue.run_once(
#            callback=self._job_callback,
#            when=timedelta(seconds=5),
#            data={
#                "chat_id": M.chat_id,
#                "message_id": msg.message_id,
#            },
#            name=f"jobtest:{M.chat_id}:{msg.message_id}",
#        )
#
#    async def _job_callback(self, context: ContextTypes.DEFAULT_TYPE) -> None:
#        data = context.job.data
#
#        await context.bot.edit_message_text(
#            chat_id=data["chat_id"],
#            message_id=data["message_id"],
#            text="✅ Job executed after 5 seconds!",
#        )
