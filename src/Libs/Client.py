from __future__ import annotations
import asyncio
from io import BytesIO
import os
from pathlib import Path
import random
import time
import pkg_resources
from typing import (
    TYPE_CHECKING,
    Iterable,
    Tuple,
    Union,
    Optional,
    List,
    Any
)

from telegram import (
    Bot,
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
    filters,
    JobQueue
)
from telegram.error import NetworkError
import httpx
from telegram.request import HTTPXRequest
from pyromod import Client as PyroClient
from dotenv import set_key
from Helpers import Utils, get_logger
from io import BytesIO
from PIL import Image

if TYPE_CHECKING:
    from pyrogram.types import User as PyroUser



class SuperClient:
    def __init__(self, config) -> None:
        from Handler import Database, CommandHandler, EventHandler

        self.config = config
        # PTB does not have a method to get a user ID from a username
        self.pyrogram_Client: PyroClient = PyroClient(
            name=config.app_name,
            api_id=config.app_id,
            api_hash=config.app_hash,
            bot_token=config.app_token,
        )
        self.bot_user_name: str = None
        self.bot_user_id: int = None
        self.bot_name: str = config.app_name
        self.prefix: str = config.prefix
        self.owner_id: int = config.owner_user_id
        self.owner_user_name: str = config.owner_user_name
        self.log = get_logger()
        self.utils = Utils(self.log, config)
        self._wtp_index = 0
        request = HTTPXRequest(
            connect_timeout=10,
            read_timeout=20,
            write_timeout=20,
            pool_timeout=10,
        )
        self._app: Application = (
            ApplicationBuilder().token(config.app_token).request(request).build()
        )
        self.bot: Bot = self._app.bot
        self.interaction_store: dict[tuple[int, int], dict[str, Any]] = {}
        self.command_handler: CommandHandler = CommandHandler(self)
        self.event_handler: EventHandler = EventHandler(self)
        self.db: Database = Database(config.url)

        self._register_handlers()

    def _register_handlers(self) -> None:
        self._app.add_handler(
            MessageHandler(filters.StatusUpdate.ALL, self._on_events)
        )
        self._app.add_handler(ChatMemberHandler(self._on_events, ChatMemberHandler.CHAT_MEMBER))
        self._app.add_handler(MessageHandler(None, self._on_message))
        self._app.add_handler(CallbackQueryHandler(self._on_message))
        
    @property
    def job_queue(self) -> Optional["JobQueue[Any]"]:
        return self._app.job_queue

    def start_whos_that_pokemon_scheduler(self) -> None:
        if self.job_queue.get_jobs_by_name("whos_that_pokemon_loop"):
            return
    
        delay = random.choice((20, 30, 40)) # seconds
    
        self.job_queue.run_once(
            SuperClient.whos_that_pokemon_job,
            when=delay*60,
            data=self,
            name="whos_that_pokemon_loop",
        )

    async def whos_that_pokemon_job(
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        self: "SuperClient" = context.job.data
    
        chats = [
            chat.chat_id
            for chat in self.db.get_all_chats()
            if chat.whos_that_pokemon
        ]
    
        if not chats:
            return
    
        chat_id = chats[self._wtp_index % len(chats)]
        self._wtp_index += 1
        pokemon_image_url: str | None = None
        pokemon_name: str | None = None
        
        for _ in range(3): 
            pokemon_image_url, pokemon_name = self.utils.get_random_pokemon()
            if pokemon_image_url and pokemon_name:
                break
        
        if not pokemon_image_url or not pokemon_name:
            self.log.warning("[WTP] Failed to get valid Pokémon after retries")
            return
        
        print(pokemon_name, pokemon_image_url)
        photo_bytes = await self.utils.generate_guess_pokemon(pokemon_image_url, pokemon_name, True)
        png_io = BytesIO(photo_bytes)
        jpeg_io = BytesIO()
        
        with Image.open(png_io) as img:
            img = img.convert("RGB")  # JPEG requires RGB
            img.save(jpeg_io, format="JPEG", quality=85, optimize=True)
        
        jpeg_io.seek(0)

        key: Tuple[int, int] = ("whos_that_pokemon", chat_id)
        now = int(time.time())
        self.interaction_store[key] = {
            "pokemon_name": pokemon_name,
            "url": pokemon_image_url,
            "sent_at": now,
            "expires_at": now + 60,
        }
        try:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=jpeg_io,
                caption="『Whos That Pokémon』\n├ Time: 60 secs\n└ Use: /guess <pokemon name>",
            )
        except (NetworkError, httpx.ReadError):
            self.log.warning(f"[WTP] Failed to send image to {chat_id}")
    
        delay = random.choice((20, 30, 40))
        self.job_queue.run_once(
            SuperClient.whos_that_pokemon_job,
            when=delay*60,
            data=self,
            name="whos_that_pokemon_loop",
        )

    async def bot_info(self) -> None:
        env_user_id = os.getenv("BOT_USER_ID")
        env_user_name = os.getenv("BOT_USER_NAME")

        if env_user_id and env_user_name:
            self.bot_user_id = int(env_user_id)
            self.bot_user_name = env_user_name
        else:
           me: User = await self.bot.get_me()
   
           self.bot_user_id = me.id
           self.bot_user_name = me.username or ""
   
           set_key(".env", "BOT_USER_ID", str(self.bot_user_id))
           set_key(".env", "BOT_USER_NAME", self.bot_user_name)

    async def _on_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        from Libs import Message
        await self.bot_info()
        msg = await Message(self, update.message or  update.callback_query).build()
        await self.command_handler.handler(msg)

    async def _on_events(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        
        from Libs import Message
        if not update.message:
            return
        
        await self.bot_info()
        msg = await Message(self, update.message).build()
        await self.event_handler.handler(msg)
        
    async def profile_photo_url(self, user_id: int) -> str:
        default_path: str = "src/Assets/image.png"
    
        db_user = self.db.get_user_by_user_id(user_id)
        avatar_url: Optional[str] = getattr(db_user, "profile_photo", None)
    
        if avatar_url:
            return avatar_url
    
        photo_id: Optional[str] = await self.get_profile_id(user_id)
        if not photo_id:
            avatar_url = self.utils.img_to_url(default_path)
            self.db.set_user_profile_photo(user_id, avatar_url)
            return avatar_url
    
        photo_path: str = await self.download_media(photo_id)
        avatar_url = self.utils.img_to_url(photo_path)
    
        try:
            os.remove(photo_path)
        except Exception:
            pass
    
        self.db.set_user_profile_photo(user_id, avatar_url)
        return avatar_url

    async def kick_chat_member(self, chat_id: Union[int, str], user_id: int ) -> None:
        await self.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await self.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
               
    async def get_profile_id(self, user_id: int) -> Optional[str]:
        try:
            photos = await self.bot.get_user_profile_photos(user_id, limit=1)
            return photos.photos[0][-1].file_id if photos.total_count > 0 else None
        except Exception as e:
            self.log.warning(
                f"[WARN][get_profile_id] Failed for {user_id}: {e}"
            )
            return None

    async def download_media(
        self,
        file_id: str,
        directory: str = "Download",
    ) -> Optional[str]:
        file = await self.bot.get_file(file_id)
    
        Path(directory).mkdir(parents=True, exist_ok=True)
    
        filename = f"{file.file_unique_id}{Path(file.file_path).suffix or '.bin'}"
        file_path = str(Path(directory) / filename)
    
        await file.download_to_drive(custom_path=file_path)
        return file_path

    async def get_users(
        self, user_name: Union[int, str, Iterable[Union[int, str]]]
    ) -> Union[PyroUser, List[PyroUser]]:
        return await self.pyrogram_Client.get_users(user_name)
    
    async def delete_message_after(
        self,
        chat_id: int,
        message_id: int,
        delay: int,
    ) -> None:
        await asyncio.sleep(delay)
        try:
            await self.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            pass

    def _log_installed_packages(self) -> None:
        installed = sorted(
            [
                (dist.project_name, dist.version)
                for dist in pkg_resources.working_set
            ],
            key=lambda x: x[0].lower(),
        )
        self.log.info("📦 Installed Python Packages in Environment:")
        for name, version in installed:
            self.log.info(f"{name}=={version}")

    def _log_ascii_banner(self, text: str = "BOT STARTED") -> None:
        banner = f"""
        ╔══════════════════════════════════╗
        ║ 🚀 {text.center(26)} 🚀 ║
        ╚══════════════════════════════════╝
        """
        self.log.info(banner)

    def run_polling(self) -> None:
        self._log_installed_packages()
        self._log_ascii_banner("TELEGRAM BOT ONLINE")
        self.command_handler.load_commands("src/Commands")
        self.start_whos_that_pokemon_scheduler()
        self.pyrogram_Client.start()
        self._app.run_polling()



