from __future__ import annotations
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
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
                "command": "convert",
                "aliases": ["tovideo", "topng"],
                "category": "sticker",
                "description": {
                    "content": "Convert a sticker or a whole pack to MP4/PNG (only 15).",
                    "usage": "<reply to sticker>",
                "OnlyChat": True,
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            reply = M.reply_to_message
            flags = context.get("flags", {})
            
            if M.is_callback and flags.get("choice"):
                return await self._process_conversion(M, flags)

            if not reply or not reply.sticker:
                return await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "『<i>Invalid Action</i>』 ❌\n"
                        "└ Reply to a sticker to convert it"
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=M.message_id,
                )

            sticker = reply.sticker
            is_animated = sticker.is_animated or sticker.is_video
            sticker_type = "Animated/Video" if is_animated else "Static"

            store_key = ("convert", M.chat_id, M.sender.user_id)
            self.client.interaction_store[store_key] = {
                "file_id": sticker.file_id,
                "set_name": sticker.set_name,
                "is_animated": is_animated,
                "msg_id": M.message_id
            }

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("『This Sticker』", callback_data="cmd:convert choice:single"),
                    InlineKeyboardButton("『Whole Pack』", callback_data="cmd:convert choice:pack")
                ]
            ])

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>Sticker Detected</i>』\n"
                    f"├ <i>Type</i>: {sticker_type}\n"
                    "└ <i>Action</i>: Choose conversion scope below."
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                reply_to_message_id=M.message_id
            )

        except Exception as e:
            error = self.client.utils.format_execution_error(e, __file__)
            await self.client.bot.send_message(M.chat_id, error, parse_mode=ParseMode.HTML)

    async def _process_conversion(self, M: Message, flags: dict):
        store_key = ("convert", M.chat_id, M.sender.user_id)
        data = self.client.interaction_store.get(store_key)
        
        if not data:
            return await self.client.bot.answer_callback_query(M.callback_id, "Session expired.", show_alert=True)

        choice = flags.get("choice")
        loading = await self.client.bot.edit_message_text(chat_id=M.chat_id, message_id=M.message_id, text="🖨")
        
        try:
            files_to_process = []
            
            if choice == "single":
                files_to_process.append(data["file_id"])
            else:
                if not data["set_name"]:
                    text = (
                        "『Invalid Sticker』 ❌\n"
                        "└ This sticker does not belong to a pack"
                    )
                    return self.client.bot.answer_callback_query(callback_query_id=M.callback_id, text=text, show_alert=True)
                s_set = await self.client.bot.get_sticker_set(data["set_name"])
                files_to_process = [s.file_id for s in s_set.stickers[:15]] 

            for f_id in files_to_process:
                input_path = await self.client.download_media(f_id)
                path_obj = Path(input_path)
                
                if data["is_animated"]:
                    output_path = path_obj.with_suffix(".mp4")
                    self.client.utils.convert_webm_or_tgs_to_mp4(str(path_obj), str(output_path))
                    await self.client.bot.send_video(M.chat_id, open(output_path, "rb"))
                else:
                    output_path = path_obj.with_suffix(".png")
                    self.client.utils.convert_webp_to_png(str(path_obj), str(output_path))
                    await self.client.bot.send_photo(M.chat_id, open(output_path, "rb"))

                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(output_path): os.remove(output_path)

            await self.client.bot.delete_message(M.chat_id, loading.message_id)
            self.client.interaction_store.pop(store_key, None)

        except Exception as e:
            error = self.client.utils.format_execution_error(e, __file__)
            await self.client.bot.send_message(M.chat_id, error, parse_mode=ParseMode.HTML)
