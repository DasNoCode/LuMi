from __future__ import annotations

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
                "command": "sticker",
                "aliases": ["s"],
                "category": "sticker",
                "description": {
                    "content": "Convert replied media to a sticker without creating a sticker set.",
                    "usage": "<reply to photo | gif | video>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        reply = M.reply_to_message
        if not reply or not (reply.photo or reply.video or reply.animation):
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="❌ Reply to a photo, GIF, or video.",
                reply_to_message_id=M.message_id,
            )
            return

        file_id: str = (
            reply.animation.file_id
            if reply.animation
            else reply.video.file_id
            if reply.video
            else reply.photo[-1].file_id
        )

        loading = await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="🔮",
            reply_to_message_id=M.message_id,
        )

        input_path: Path | None = None
        output_path: Path | None = None

        try:
            input_path = Path(await self.client.download_media(file_id))

            is_video: bool = bool(reply.video or reply.animation)
            output_path = (
                input_path.with_suffix(".webm")
                if is_video
                else input_path.with_suffix(".webp")
            )

            if is_video:
                self.client.utils.video_to_webm(input_path, output_path)
            else:
                self.client.utils.image_to_webp(input_path, output_path)

            await self.client.bot.send_sticker(
                chat_id=M.chat_id,
                sticker=output_path.open("rb"),
                reply_to_message_id=M.message_id,
            )

        finally:
            try:
                await self.client.bot.delete_message(
                    chat_id=M.chat_id,
                    message_id=loading.message_id,
                )
                if input_path:
                    input_path.unlink(missing_ok=True)
                if output_path:
                    output_path.unlink(missing_ok=True)
            except Exception:
                pass