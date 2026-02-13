from __future__ import annotations

import traceback
from typing import Union, Optional, List, Dict, Any, TYPE_CHECKING, Tuple
from telegram import (
    CallbackQuery,
    Message as PTBMessage,
    ChatMemberUpdated,
)
from telegram.constants import ChatType, ChatMemberStatus
from Helpers.JsonObject import JsonObject
from telegram.error import NetworkError, TimedOut
if TYPE_CHECKING:
    from telegram import Chat, User, ChatMember
    from Libs import SuperClient


class Message:
    
    def __init__(
        self,
        client: SuperClient,
        data: Union[PTBMessage, CallbackQuery, ChatMemberUpdated],
    ) -> None:
        self._client: SuperClient = client
        self.is_callback: bool = isinstance(data, CallbackQuery)
        self.is_event: bool = isinstance(data, PTBMessage) and (
            getattr(data, "new_chat_members", None)
            or getattr(data, "left_chat_member", None)
        )

        self._m: Optional[PTBMessage] = (
            data.message
            if self.is_callback
            else (data if isinstance(data, PTBMessage) else None)
        )

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

        if isinstance(data, ChatMemberUpdated):
            self.sender_raw: Optional[User] = data.from_user
        elif self.is_callback:
            self.sender_raw = data.from_user
        else:
            self.sender_raw = getattr(self._m, "from_user", None)

        self.message_id: Optional[int] = getattr(self._m, "message_id", None)

        if self.is_callback:
            self.callback_id: int = data.id
            self.message: str = data.data or ""
        else:
            self.message = (
                getattr(self._m, "caption", None) or getattr(self._m, "text", "") or ""
            )

        self.reply_to_message: Optional[PTBMessage] = getattr(
            self._m, "reply_to_message", None
        )

        self.event_type: Optional[str] = None
        self.event_user: Optional[JsonObject] = None
        self.action_by: Optional[JsonObject] = None

        if self.is_event:
            self._greeting()

        self.sender: Optional[JsonObject] = None
        self.reply_to_user: Optional[JsonObject] = None
        self.msg_type: Optional[str] = None
        self.file_id: Optional[str] = None
        self.mentions: List[JsonObject] = []

    async def _get_mentioned_users(self, text: str) -> List[JsonObject]:
        mentions: List[JsonObject] = []

        for word in text.split():
            if not word.startswith("@"):
                continue
            try:
                user: User = await self._client.pyrogram_Client.get_users(word)
                full_name: str = (
                    f"{user.first_name or ''} {user.last_name or ''}".strip()
                )
                mentions.append(
                    JsonObject(
                        {
                            "user_id": user.id,
                            "mention": self.mention(user),
                            "is_bot": user.is_bot,
                            "user_full_name": full_name
                        }
                    )
                )
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                self._client.log.error(f"[ERROR] {tb.filename.split('/')[-1]}: {tb.lineno} | {e}")

        return mentions

    def _extract_media(self) -> None:
        target = self.reply_to_message or self._m
        if not target: return
        
        attach = target.effective_attachment
        if attach:
            if isinstance(attach, (list, tuple)):
                self.file_id = attach[-1].file_id
            else:
                self.file_id = attach.file_id
            for t in ["photo", "video", "animation", "sticker", "audio", "voice"]:
                if getattr(target, t, None):
                    self.msg_type = t
                    break

                
    def mention(self, u: Any) -> str:
        username = getattr(u, "username", None) or getattr(u, "user_name", None)
        user_id = getattr(u, "id", None) or getattr(u, "user_id", None)
        full_name = getattr(u, "full_name", None) or getattr(u, "user_full_name", "")
    
        if username:
            return f"@{username}"
    
        return f'<a href="tg://user?id={user_id}">{full_name}</a>'
    
    async def build(self) -> Message:
        if self.is_event:
            return self

        self._extract_media()

        if self.sender_raw:
            self.sender = JsonObject(
                {
                    "user_id": self.sender_raw.id,
                    "mention": self.mention(self.sender_raw),
                    "is_bot": self.sender_raw.is_bot,
                    "user_full_name": self.sender_raw.full_name
                }
            )

        if self.reply_to_message and getattr(self.reply_to_message, "from_user", None):
            reply_user: User = self.reply_to_message.from_user
            if reply_user.id != (self.sender_raw.id if self.sender_raw else 0):
                self.reply_to_user = JsonObject(
                    {
                        "user_id": reply_user.id,
                        "mention": self.mention(reply_user),
                        "is_bot": reply_user.is_bot,
                        "user_full_name": reply_user.full_name
                    }
                )
        for word in (self.message).split():
            if not word.startswith("@"):
                self.mentions = await self._get_mentioned_users(self.message)
        return self

    def _greeting(self) -> None:
        m: Optional[PTBMessage] = self._m
        if not m:
            return

        if getattr(m, "new_chat_members", None):
            user: User = m.new_chat_members[0]
            self.event_type = "join"
            self.event_user = JsonObject(
                {
                    "user_id": user.id,
                    "mention": self.mention(user),
                    "is_bot": user.is_bot,
                    "user_full_name": user.full_name,
                }
            )
            if m.from_user and m.from_user.id != user.id:
                self.action_by = JsonObject(
                    {
                        "user_id": m.from_user.id,
                        "mention": self.mention(m.from_user),
                        "is_bot": m.from_user.is_bot,
                        "user_full_name": m.from_user.full_name,
                    }
                )

        elif getattr(m, "left_chat_member", None):
            user: User = m.left_chat_member
            self.event_type = (
                "kick" if (m.from_user and m.from_user.id != user.id) else "leave"
            )
            self.event_user = JsonObject(
                {
                    "user_id": user.id,
                    "mention": self.mention(user),
                    "is_bot": user.is_bot,
                    "user_full_name": user.full_name,
                }
            )
            if self.event_type == "kick":
                self.action_by = JsonObject(
                    {
                        "user_id": m.from_user.id,
                        "mention": self.mention(m.from_user),
                        "is_bot": m.from_user.is_bot,
                        "user_full_name": m.from_user.full_name,
                    }
                )