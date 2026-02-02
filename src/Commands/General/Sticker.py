from __future__ import annotations

from pathlib import Path
from Libs import BaseCommand
from typing import Any, TYPE_CHECKING
from telegram.error import BadRequest
from telegram import InputSticker
from telegram.constants import StickerFormat


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
                "category": "general",
                "description": {"content": "Convert media to sticker"},
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        if not M.reply_to_message or not M.reply_to_message.photo[0].file_id:
            return

        user_id = M.sender.user_id

        emoji: str = "✨"

        input_path = Path(
            await self.client.download_media(M.reply_to_message.photo[0].file_id)
        )

        suffix = input_path.suffix.lower()
        is_video = suffix in {".gif", ".mp4"}
        
        bot_username = self.client.bot.username.lower()
        
        pack_type = "video" if is_video else "static"
        
        pack_name = f"pack_{user_id}_{pack_type}_by_{bot_username}"

        
        
        output_path = (
            input_path.with_suffix(".webm")
            if is_video
            else input_path.with_suffix(".webp")
        )

        # ---- convert media ----
        if is_video:
            self.client.utils.video_to_webm(input_path, output_path)
        else:
            self.client.utils.image_to_webp(input_path, output_path)

        sticker = InputSticker(
            sticker=output_path.open("rb"),
            emoji_list=[emoji],
            format=StickerFormat.VIDEO if is_video else StickerFormat.STATIC
        )

        # ---- check pack ----
        try:
            await self.client.bot.get_sticker_set(pack_name)
            pack_exists = True
        except BadRequest as e:
            if "Sticker_set_not_found" in str(e):
                pack_exists = False
            else:
                raise

        # ---- create / add ----
        if not pack_exists:
            await self.client.bot.create_new_sticker_set(
                user_id=user_id,
                name=pack_name,
                title=pack_title,
                stickers=[sticker],
            )
        else:
            await self.client.bot.add_sticker_to_set(
                user_id=user_id,
                name=pack_name,
                sticker=sticker,
            )

        await self.client.send_message(
            chat_id=M.chat_id,
            text=f"✅ Sticker added to pack:\n<code>{pack_name}</code>",
            reply_to_message_id=M.message_id,
        )
