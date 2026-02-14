from __future__ import annotations
import asyncio
from io import BytesIO
import os
from pathlib import Path
import random
import time
import traceback
from typing import (
    Dict,
    Tuple,
    Union,
    Optional,
    Any
)
from Helpers.JsonObject import JsonObject
from httpx import NetworkError
from telegram import (
    Bot,
    ChatMember,
    Update,
    User
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ChatMemberHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatMemberStatus
from telegram.request import HTTPXRequest
from pyromod import Client as PyroClient
from dotenv import set_key
from Helpers import Utils, get_logger
from io import BytesIO
from PIL import Image

class SuperClient:
    def __init__(self, config) -> None:
        from Handler import Database, CommandHandler, EventHandler

        self.config = config
        self.log = get_logger()
        self.utils = Utils(self.log, config)
        
        self.pyrogram_Client = PyroClient(
            name=config.app_name,
            api_id=config.app_id,
            api_hash=config.app_hash,
            bot_token=config.app_token,
        )
        
        request = HTTPXRequest(connect_timeout=10, read_timeout=20)
        self._app: Application = (
            ApplicationBuilder().token(config.app_token).request(request).build()
        )
        self.bot: Bot = self._app.bot
        
        self.bot_user_name: Optional[str] = os.getenv("BOT_USER_NAME")
        self.bot_user_id: Optional[int] = int(os.getenv("BOT_USER_ID")) if os.getenv("BOT_USER_ID") else None
        self.prefix: str = config.prefix
        self.bot_name: str = config.app_name
        
        self.db = Database(config.url, self)
        self.command_handler = CommandHandler(self)
        self.event_handler = EventHandler(self)
        self.interaction_store: dict[tuple[str, int], dict[str, Any]] = {}
        self._wtp_index = 0
        
        self._register_handlers()

    def _register_handlers(self) -> None:
        self._app.add_handler(MessageHandler(filters.StatusUpdate.ALL , self._handle_update))
        self._app.add_handler(ChatMemberHandler(self._handle_update, ChatMemberHandler.CHAT_MEMBER))
        
        self._app.add_handler(MessageHandler(None, self._handle_update))
        self._app.add_handler(CallbackQueryHandler(self._handle_update))

    async def _handle_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        from Libs import Message
        data = update.message or update.callback_query or update.my_chat_member or update.chat_member
        if not data:
            return

        msg = await Message(self, data).build()
        if msg.is_event:
            await self.event_handler.handler(msg)
        else:
            await self.command_handler.handler(msg)

    async def get_user_permissions(
        self,
        chat_id: int,
        user_id: int,
    ) -> Tuple[ChatMemberStatus, Optional[Dict[str, bool]]]:
        try:
            member = await self.bot.get_chat_member(chat_id, user_id)
            
            if member.status == ChatMemberStatus.OWNER:
                return member.status, None
            if member.status == ChatMemberStatus.ADMINISTRATOR:
                return member.status, {
                    "can_change_info": member.can_change_info,
                    "can_delete_messages": member.can_delete_messages,
                    "can_invite_users": member.can_invite_users,
                    "can_promote_members": member.can_promote_members,
                    "can_restrict_members": member.can_restrict_members,
                    "can_pin_messages": getattr(member, "can_pin_messages", False)
                }
            return member.status, None
        except NetworkError as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                self.client.log.error(f"[ERROR] {tb.filename.split('/')[-1]}: {tb.lineno} | {e}")

    async def whos_that_pokemon_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        chats = [c.chat_id for c in self.db.get_all_chats() if getattr(c, "whos_that_pokemon", False)]
        if not chats: return

        chat_id = chats[self._wtp_index % len(chats)]
        self._wtp_index += 1

        pokemon_data = self.utils.get_random_pokemon()
        if not pokemon_data: return
        img_url, name = pokemon_data

        photo_bytes = await self.utils.generate_guess_pokemon(img_url, name, True)
        
        with Image.open(BytesIO(photo_bytes)) as img:
            jpeg_io = BytesIO()
            img.convert("RGB").save(jpeg_io, "JPEG", quality=80)
            jpeg_io.seek(0)

        self.interaction_store[("wtp", chat_id)] = {
            "name": name, 
            "expires_at": time.time() + 60
        }

        try:
            caption: str = (
                "『<i>Whos That Pokémon</i>』🧩\n"
                "├ <i>Time</i>: 60s\n"
                "└ <i>Use</i>: /guess [ <i>pokemon name</i> ]"
            )
            print(name)
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=jpeg_io,
                caption=caption,
                parse_mode="HTML"
            )
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            self.log.error(f"[ERROR] {tb.filename.split('/')[-1]}: {tb.lineno} | {e}")
            
        delay: int = random.randint(30, 60)*60
        context.job_queue.run_once(self.whos_that_pokemon_job, when=delay)

    async def initialize_bot(self) -> None:
        if not self.bot_user_id:
            me: User = await self.bot.get_me()
            self.bot_user_id = me.id
            self.bot_user_name = me.username
            set_key(".env", "BOT_USER_ID", str(self.bot_user_id))
            set_key(".env", "BOT_USER_NAME", self.bot_user_name)
        
        self.log.info(f"Connected as @{self.bot_user_name} ({self.bot_user_id})")

    async def kick_chat_member(self, chat_id: Union[int, str], user_id: int ) -> None:
        await self.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await self.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)

    async def get_profile_id(self, user_id: int) -> Optional[str]:
        try:
            photos = await self.bot.get_user_profile_photos(user_id, limit=1)
            return photos.photos[0][-1].file_id if photos.total_count > 0 else None
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            self.log.error(f"[ERROR] {tb.filename.split('/')[-1]}: {tb.lineno} | {e}")
            return None

    async def download_media(self, file_id: str) -> Optional[str]:
        file = await self.bot.get_file(file_id)
        out_path = Path("Downloads") / f"{file.file_unique_id}{Path(file.file_path).suffix}"
        out_path.parent.mkdir(exist_ok=True)
        
        await file.download_to_drive(custom_path=str(out_path))
        return str(out_path)
                
    def run_polling(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.initialize_bot())
        self.command_handler.load_commands("src/Commands")
        if self._app.job_queue:
            self._app.job_queue.run_once(self.whos_that_pokemon_job, when=(random.randint(30, 60)*60))
        self.pyrogram_Client.start()
        self._app.run_polling()



