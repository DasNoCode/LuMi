from __future__ import annotations

from typing import Union, Optional, List, Dict, Any, TYPE_CHECKING
from telegram import CallbackQuery, ChatPermissions, Message as PTBMessage, ChatMemberUpdated
from telegram.constants import ChatType, ChatMemberStatus
from Helpers.JsonObject import JsonObject

if TYPE_CHECKING:
    from telegram import Chat, User
    from Libs import SuperClient


class Message:
    _media_types: List[str] = [
        "voice", "animation", "audio", "photo",
        "video", "document", "video_note", "sticker",
    ]

    def __init__(
        self,
        client: SuperClient,
        data: Union[PTBMessage, CallbackQuery, ChatMemberUpdated],
    ) -> None:
        # --- Core references ---
        self._client: SuperClient = client
        self.is_callback: bool = isinstance(data, CallbackQuery)
        self.is_event: bool = isinstance(data, PTBMessage) and (
            getattr(data, "new_chat_members", None)
            or getattr(data, "left_chat_member", None)
        )
        self._m: Optional[PTBMessage] = (
            data.message if self.is_callback else (data if isinstance(data, PTBMessage) else None)
        )

        # --- Chat info ---
        self.chat: Optional[Chat]
        self.chat_id: int
        self.chat_type: str
        self.chat_title: Optional[str]
        self.chat_permissions: Optional[Dict[str, bool]] = None
        if self._m:
            self.chat = self._m.chat
            self.chat_id = self.chat.id
            self.chat_type = self.chat.type
            self.chat_title = (
                self.chat.title if self.chat.type != ChatType.PRIVATE else None
            )
        else:
            self.chat = None
            self.chat_id = 0
            self.chat_type = ""
            self.chat_title = None

        # --- Sender info ---
        if isinstance(data, ChatMemberUpdated):
            self.sender_raw: Optional[User] = data.from_user
        elif self.is_callback:
            self.sender_raw: Optional[User] = data.from_user
        else:
            self.sender_raw: Optional[User] = getattr(self._m, "from_user", None)

        # --- Common message attributes ---
        self.message_id: Optional[int] = getattr(self._m, "message_id", None)
        if self.is_callback:
            self.message = data.data or ""
        else:
            self.message = (
                getattr(self._m, "caption", None)
                or getattr(self._m, "text", "")
                or ""
            )
        self.reply_to_message: Optional[PTBMessage] = getattr(self._m, "reply_to_message", None)
        # --- Event handling attributes ---
        self.event_type: Optional[str] = None  # "join", "leave", "kick"
        self.event_user: Optional[JsonObject] = None
        self.action_by: Optional[JsonObject] = None

        if self.is_event:
            self._greeting()

        # --- General message attributes ---
        self.sender: Optional[JsonObject] = None
        self.reply_to_user: Optional[JsonObject] = None
        self.msg_type: Optional[str] = None
        self.file_id: Optional[str] = None
        self.is_self: bool = False
        self.bot_username: Optional[str] = None
        self.bot_user_id: Optional[int] = None
        self.bot_is_admin: bool = False
        self.user_status: Optional[str] = None
        self.is_admin: bool = False
        self.urls: List[str] = []
        self.numbers: List[int] = []
        self.mentioned: List[JsonObject] = []
        self.user_roles: Dict[int, str] = {}

    def _greeting(self) -> None:
        m: Optional[PTBMessage] = self._m
        if not m:
            return

        # Someone joined (invited or via link)
        if getattr(m, "new_chat_members", None):
            user: User = m.new_chat_members[0]
            self.event_type = "join"
            self.event_user = JsonObject({
                "user_id": user.id,
                "user_name": user.username,
                "user_full_name": user.full_name,
            })
            if m.from_user and m.from_user.id != user.id:
                self.action_by = JsonObject({
                    "user_id": m.from_user.id,
                    "user_name": m.from_user.username,
                    "user_full_name": m.from_user.full_name,
                })

        # Someone left or was removed
        elif getattr(m, "left_chat_member", None):
            user: User = m.left_chat_member
            self.event_type = (
                "kick" if (m.from_user and m.from_user.id != user.id) else "leave"
            )
            self.event_user = JsonObject({
                "user_id": user.id,
                "user_name": user.username,
                "user_full_name": user.full_name,
            })
            if self.event_type == "kick":
                self.action_by = JsonObject({
                    "user_id": m.from_user.id,
                    "user_name": m.from_user.username,
                    "user_full_name": m.from_user.full_name,
                })
                
    async def _get_chat_permissions(self) -> Optional[ChatPermissions]:
        chat: Chat = await self._client.bot.get_chat(self.chat_id)
        return chat.permissions
    
    async def _get_profile_id(self, user_id: int) -> Optional[str]:
        try:
            photos = await self._client.bot.get_user_profile_photos(user_id, limit=1)
            return photos.photos[0][-1].file_id if photos.total_count > 0 else None
        except Exception as e:
            self._client.log.warning(f"[WARN][_get_profile_id] Failed for {user_id}: {e}")
            return None

    async def _get_user_permissions(self, user_id: int) -> Optional[Dict[str, bool]]:
        if self.chat_type == ChatType.PRIVATE:
            return None
        try:
            member = await self._client.get_chat_member(self.chat_id, user_id)
            if member.status == ChatMemberStatus.ADMINISTRATOR:
                return {
                    "can_change_info": member.can_change_info,
                    "can_delete_messages": member.can_delete_messages,
                    "can_invite_users": member.can_invite_users,
                    "can_pin_messages": member.can_pin_messages,
                    "can_promote_members": member.can_promote_members,
                    "can_restrict_members": member.can_restrict_members,
                }
        except Exception as e:
            self._client.log.warning(f"[WARN][_get_user_permissions] for {user_id}: {e}")
        return None

    async def _get_user_role(self, user_id: int) -> str:
        if self.chat_type == ChatType.PRIVATE:
            return "user"
        try:
            member = await self._client.get_chat_member(self.chat_id, user_id)
            if member.status == ChatMemberStatus.OWNER:
                return "owner"
            elif member.status == ChatMemberStatus.ADMINISTRATOR:
                return "admin"
        except Exception as e:
            self._client.log.warning(f"[WARN][_get_user_role] Could not fetch role for {user_id}: {e}")
        return "member"

    async def _get_mentioned_users(self, text: str) -> List[JsonObject]:
        mentioned: List[JsonObject] = []
        for word in text.split():
            if not word.startswith("@"):
                continue
            try:
                user: User = await self._client.get_users(word)
                full_name: str = f"{user.first_name or ''} {user.last_name or ''}".strip()
                profile_id: Optional[str] = await self._get_profile_id(user.id)
                role: str = await self._get_user_role(user.id)
                perms: Optional[Dict[str, bool]] = await self._get_user_permissions(user.id)

                self.user_roles[user.id] = role

                mentioned.append(
                    JsonObject({
                        "user_id": user.id,
                        "user_name": user.username,
                        "user_full_name": full_name,
                        "user_profile_id": profile_id,
                        "user_role": role,
                        "permissions": perms,
                    })
                )
            except Exception as e:
                self._client.log.error(f"[ERROR][_get_mentioned_users] Could not resolve {word}: {e}")
        return mentioned

    def _extract_media(self) -> None:
        def _get_file_id(media: Any) -> Optional[str]:
            if isinstance(media, (list, tuple)) and media:
                return media[-1].file_id
            return getattr(media, "file_id", None)

        for src in (self.reply_to_message, self._m):
            if not src:
                continue
            for mtype in self._media_types:
                media: Any = getattr(src, mtype, None)
                if not media:
                    continue
                file_id: Optional[str] = _get_file_id(media)
                if file_id:
                    self.msg_type = mtype
                    self.file_id = file_id
                    return

    async def build(self) -> Message:
        if self.is_event:
            return self

        me: User = await self._client.get_me()
        self.bot_userid: int = me.id
        self.bot_username: str = me.username
        self.is_self = self.sender_raw is not None and self.sender_raw.id == me.id
        
        await self._get_chat_permissions()

        self._extract_media()

        self.urls = self._client.utils.get_urls(self.message)
        self.numbers = self._client.utils.extract_numbers(self.message)

        # --- Sender ---
        if self.sender_raw:
            sender_role: str = await self._get_user_role(self.sender_raw.id)
            sender_profile_id: Optional[str] = await self._get_profile_id(self.sender_raw.id)
            sender_perms: Optional[Dict[str, bool]] = await self._get_user_permissions(self.sender_raw.id)
            self.user_roles[self.sender_raw.id] = sender_role
            self.sender = JsonObject({
                "user_id": self.sender_raw.id,
                "user_name": self.sender_raw.username,
                "user_full_name": self.sender_raw.full_name,
                "user_profile_id": sender_profile_id,
                "user_role": sender_role,
                "permissions": sender_perms,
            })

        # --- Reply-to user ---
        if self.reply_to_message and getattr(self.reply_to_message, "from_user", None):
            reply_user: User = self.reply_to_message.from_user
            if reply_user.id != (self.sender_raw.id if self.sender_raw else 0):
                role: str = await self._get_user_role(reply_user.id)
                profile_id: Optional[str] = await self._get_profile_id(reply_user.id)
                perms: Optional[Dict[str, bool]] = await self._get_user_permissions(reply_user.id)
                self.user_roles[reply_user.id] = role
                self.reply_to_user = JsonObject({
                    "user_id": reply_user.id,
                    "user_name": reply_user.username,
                    "user_full_name": reply_user.full_name,
                    "user_profile_id": profile_id,
                    "user_role": role,
                    "permissions": perms,
                })

        # --- Bot admin check ---
        if self.chat_type != ChatType.PRIVATE and self.bot_userid:
            try:
                bot_member = await self._client.get_chat_member(self.chat_id, self.bot_userid)
                self.bot_is_admin = bot_member.status in {
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                }
            except Exception as e:
                self._client.log.warning(f"[WARN][build] Could not fetch bot admin status: {e}")

        # --- User admin check ---
        if self.sender_raw:
            sender_role: Optional[str] = self.user_roles.get(self.sender_raw.id)
            self.is_admin = sender_role in {"admin", "owner"}

        # --- Mentions ---
        self.mentioned = await self._get_mentioned_users(self.message)
        if self.reply_to_user:
            self.mentioned.append(self.reply_to_user)

        return self
