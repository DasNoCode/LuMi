from __future__ import annotations
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, Dict, List

from Libs import BaseCommand
from telegram import InputSticker, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import StickerFormat
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
                "command": "stickerset",
                "aliases": ["createset", "newpack", "sset"],
                "category": "sticker",
                "description": {
                    "content": "Create or add to a sticker set from replied media.",
                    "usage": "<reply> emoji:✨ title:My Pack",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        text: str = context.get("text", "").strip()

        emoji: str = flags.get("emoji") or (text.split()[0] if text else "✨")
        title_flag: str | None = flags.get("title")

        store_key = ("sticker", M.chat_id, M.sender.user_id)
        user_sets: List[Dict[str, Any]] = self.client.db.get_user_sticker_sets(M.sender.user_id)

        if M.is_callback:
            store = self.client.interaction_store.get(store_key)
            if not store:
                text = (
                    "『<i>Session Expired</i>』⏳\n"
                    "└ <i>Status</i>: Please start again"
                )
                return await self.client.bot.answer_callback_query(chat_id=M.callback_id, text=text, show_alert=True)

            selected_set = flags.get("set")
            force_new = flags.get("new") == "true"
            
            if selected_set:
                target_pack = next((s for s in user_sets if s["pack_name"] == selected_set), None)
                if target_pack:
                    is_video_pack = target_pack["format"] == "video"
                    if is_video_pack != store["is_video"]:
                        text = (
                            "『<i>Format Mismatch</i>』❌\n"
                            "└ <i>Status</i>: Format Mismatch!"
                        )
                        return await self.client.bot.answer_callback_query(
                            chtat_id=M.callback_id, text=text, show_alert=True
                        )

            file_id = store["file_id"]
            is_video = store["is_video"]
            is_native_sticker = store["is_native"]
            is_animated = store.get("is_animated", False) 
            emoji = store["emoji"]
            pack_title = store["title"] or f"{M.sender.user_full_name}'s Pack"
            origin_msg_id = store["origin_msg_id"]

            try: await self.client.bot.delete_message(chat_id=M.chat_id, message_id=M.message_id)
            except: pass
        else:
            reply = M.reply_to_message
            if not reply or not (reply.photo or reply.video or reply.animation or reply.sticker):
                text = (
                    "『<i>Invalid Action</i>』❌ \n"
                    "└ <i>Instruction</i>: Reply to a photo, video, GIF, or sticker"
                )
                return await self.client.bot.send_message(parse_mode="HTML", chat_id=M.chat_id, text=text)

            is_native_sticker = bool(reply.sticker)
            is_animated = bool(reply.sticker and reply.sticker.is_animated)
            
            is_video = bool(reply.video or reply.animation or (reply.sticker and (reply.sticker.is_video or reply.sticker.is_animated)))
            
            file_id = (
                reply.sticker.file_id if reply.sticker 
                else reply.animation.file_id if reply.animation 
                else reply.video.file_id if reply.video 
                else reply.photo[-1].file_id
            )

            origin_msg_id = M.message_id
            pack_title = title_flag or f"{M.sender.user_full_name}'s Pack"

            self.client.interaction_store[store_key] = {
                "file_id": file_id, "is_video": is_video, "is_native": is_native_sticker,
                "is_animated": is_animated, "emoji": emoji, "title": pack_title, "origin_msg_id": origin_msg_id,
            }

            if user_sets:
                buttons = []
                row = []
                for s in user_sets:
                    row.append(InlineKeyboardButton(text=f"『{s['pack_title']}』", callback_data=f"cmd:stickerset set:{s['pack_name']}"))
                    if len(row) == 2: buttons.append(row); row = []
                if row: buttons.append(row)
                buttons.append([InlineKeyboardButton(text="『New Set』", callback_data="cmd:stickerset new:true")])
                text = (
                    "『<i>Choose a Pack</i>』 📦\n"
                    "├ Select an existing pack\n"
                    "└ Or create a new one below"
                )
                return await self.client.bot.send_message(parse_mode="HTML", chat_id=M.chat_id, text=text, reply_markup=InlineKeyboardMarkup(buttons))

            selected_set, force_new = None, True

        loading = await self.client.bot.send_message(M.chat_id, "⌛", reply_to_message_id=origin_msg_id)
        input_path, output_path = None, None

        try:
            raw_path = await self.client.download_media(file_id)
            input_path = Path(raw_path)
            pack_type = "video" if is_video else "static"

            if force_new or not selected_set:
                pack_name = f"pack_{self.client.utils.random_text()}_{M.sender.user_id}_{pack_type}_by_{self.client.bot_user_name}"
            else:
                pack_name = selected_set

            if is_native_sticker:
                output_path = input_path
            else:
                output_path = input_path.with_suffix(".webm" if is_video else ".webp")
                if is_video:
                    self.client.utils.video_to_webm(input_path, output_path)
                else:
                    self.client.utils.image_to_webp(input_path, output_path)

            s_format = StickerFormat.STATIC
            if is_animated: s_format = StickerFormat.ANIMATED
            elif is_video: s_format = StickerFormat.VIDEO

            sticker = InputSticker(
                sticker=open(output_path, "rb"),
                emoji_list=[emoji],
                format=s_format
            )

            try:
                await self.client.bot.add_sticker_to_set(user_id=M.sender.user_id, name=pack_name, sticker=sticker)
            except BadRequest as e:
                if "Sticker set not found" in str(e) or force_new:
                    await self.client.bot.create_new_sticker_set(
                        user_id=M.sender.user_id,
                        name=pack_name,
                        title=pack_title,
                        stickers=[sticker],
                        sticker_type="regular"
                    )
                else: raise e

            self.client.db.add_sticker_sets(pack_name=pack_name, pack_title=pack_title, format=pack_type, creator_user_id=M.sender.user_id)
            
            sticker_set = await self.client.bot.get_sticker_set(pack_name)
            await self.client.bot.delete_message(M.chat_id, loading.message_id)
            await self.client.bot.send_sticker(M.chat_id, sticker_set.stickers[-1].file_id, reply_to_message_id=origin_msg_id)

        finally:
            if input_path and input_path.exists(): input_path.unlink()
            if output_path and output_path.exists() and output_path != input_path: output_path.unlink()
