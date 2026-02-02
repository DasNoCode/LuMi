from __future__ import annotations

import subprocess
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
                "command": "jobtest",
                "category": "general",
                "description": {"content": "Convert MP4 to WebM"},
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        print(M.reply_to_message.photo[0].file_id)
        return
        input_path: Path = Path("Download/animation.gif.mp4")
        output_path: Path = Path("Download/output.webm")

        crf: int = 30
        fps: int = 30

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-vf",
                f"scale=trunc(iw/2)*2:trunc(ih/2)*2,fps={fps}",
                "-c:v",
                "libvpx-vp9",
                "-b:v",
                "0",
                "-crf",
                str(crf),
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(output_path),
            ],
            check=True,
        )

        await self.client.bot.send_sticker(
            chat_id=M.chat_id,
            sticker=str(output_path),
            reply_to_message_id=M.message_id,
        )
