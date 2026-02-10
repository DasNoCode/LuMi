from datetime import datetime
from typing import Optional, Any, Dict, List
from pymodm import connect
from pymodm.errors import DoesNotExist
from telegram import ChatPermissions

from Models import User, Chat, Bot


class Database:
    def __init__(self, url: str):
        connect(url)

    @staticmethod
    def now() -> float:
        return datetime.now()


    # ---Chat DB functions---
    def _update_or_create_group(self, chat_id: int, updates: Dict[str, Any]) -> None:
        try:
            chat = Chat.objects.raw({"chat_id": chat_id}).first()
            for key, value in updates.items():
                setattr(chat, key, value)
            chat.save()
        except DoesNotExist:
            updates["chat_id"] = chat_id
            Chat(**updates).save()

    def get_all_chats(self) -> List[Chat]:
        return list(Chat.objects.all())

    def get_group_by_chat_id(self, chat_id: int) -> Chat:
        try:
            return Chat.objects.raw({"chat_id": chat_id}).first()
        except DoesNotExist:
            chat = Chat(chat_id=chat_id)
            chat.save()
            return chat

    def set_greetings(self, chat_id: int, events_status: bool) -> None:
        self._update_or_create_group(chat_id, {"events": events_status})

    def set_group_mod(self, chat_id: int, mod_status: bool) -> None:
        self._update_or_create_group(chat_id, {"mod": mod_status})

    def chat_perms(self, chat_id: int, perms: ChatPermissions) -> None:
        permissions: Dict[str, bool] = {
            "can_send_messages": perms.can_send_messages,
            "can_send_photos": perms.can_send_photos,
            "can_send_videos": perms.can_send_videos,
            "can_send_audios": perms.can_send_audios,
            "can_send_documents": perms.can_send_documents,
            "can_send_voice_notes": perms.can_send_voice_notes,
            "can_send_video_notes": perms.can_send_video_notes,
            "can_send_polls": perms.can_send_polls,
            "can_send_other_messages": perms.can_send_other_messages,
            "can_add_web_page_previews": perms.can_add_web_page_previews,
            "can_invite_users": perms.can_invite_users,
            "can_pin_messages": perms.can_pin_messages,
            "can_change_info": perms.can_change_info,
            "can_manage_topics": perms.can_manage_topics,
        }

        chat = self.get_group_by_chat_id(chat_id)
        current = getattr(chat, "permissions", {}) or {}
        current.update(permissions)

        self._update_or_create_group(chat_id, {"permissions": current})

    def add_warn(
        self,
        chat_id: int,
        user_full_name: str,
        user_id: int,
        by_user_id: int,
        reason: str | None = None,
    ) -> int:
        chat = self.get_group_by_chat_id(chat_id)
        warns: List[Dict[str, Any]] = list(chat.warns or [])

        for i, entry in enumerate(warns):
            if entry["user_id"] == user_id:
                count = min(entry.get("count", 0) + 1, 3)
                warns[i] = {
                    "user_full_name": user_full_name,
                    "user_id": user_id,
                    "by_user_id": by_user_id,
                    "count": count,
                    "reasons": entry.get("reasons", []) + ([reason] if reason else []),
                }
                chat.warns = warns
                chat.save()
                return count

        warns.append(
            {   "user_full_name": user_full_name,
                "user_id": user_id,
                "by_user_id": by_user_id,
                "count": 1,
                "reasons": [reason] if reason else [],
            }
        )

        chat.warns = warns
        chat.save()
        return 1

    def manage_banned_user(
        self,
        chat_id: int,
        user_id: int,
        by_user_id: int,
        ban: bool,
        reason: Optional[str] = None,
    ) -> bool:
        chat = self.get_group_by_chat_id(chat_id)
        banned: List[Dict[str, Any]] = list(chat.banned_users or [])

        if ban:
            if any(entry["user_id"] == user_id for entry in banned):
                return False

            banned.append(
                {
                    "user_id": user_id,
                    "by": by_user_id,
                    "date": datetime.now(),
                    "reason": reason,
                }
            )
            chat.banned_users = banned
            chat.save()
            return True

        for entry in banned:
            if entry["user_id"] == user_id:
                banned.remove(entry)
                chat.banned_users = banned
                chat.save()
                return True

        return False
    
    def set_whos_that_pokemon(
        self,
        chat_id: int,
        enabled: bool,
    ) -> None:
        self._update_or_create_group(
            chat_id,
            {"whos_that_pokemon": enabled},
        )
    # ---User DB functions---

    def _update_or_create_user(self, user_id: int, updates: Dict[str, Any]) -> None:
        try:
            user = User.objects.raw({"user_id": str(user_id)}).first()
            for key, value in updates.items():
                setattr(user, key, value)
            user.save()
        except DoesNotExist:
            updates["user_id"] = str(user_id)
            User(**updates).save()

    def get_user_by_user_id(self, user_id: int) -> User:
        try:
            return User.objects.raw({"user_id": str(user_id)}).first()
        except DoesNotExist:
            self._update_or_create_user(user_id, {})
            return User.objects.raw({"user_id": str(user_id)}).first()

    def update_user_ban(
        self,
        user_id: int,
        status: bool,
        reason: str | None = None,
    ) -> None:
        self._update_or_create_user(
            user_id,
            {
                "ban": {
                    "status": status,
                    "reason": reason,
                    "since": self.now().second if status else None,
                }
            },
        )

    def set_user_afk(
        self,
        user_id: int,
        *,
        status: bool | None = None,
        reason: str | None = None,
        mentioned_msg_id: int | None = None,
    ) -> None:
        user = self.get_user_by_user_id(user_id)
        afk_data: Dict[str, Any] = getattr(user, "afk", {}) or {}

        if status is not None:
            afk_data["status"] = status
            afk_data["reason"] = reason
            afk_data["duration"] = self.now().second if status else None
            afk_data["mentioned_msgs"] = (
                [] if not status else afk_data.get("mentioned_msgs", [])
            )

        if mentioned_msg_id is not None:
            afk_data.setdefault("mentioned_msgs", []).append(mentioned_msg_id)

        self._update_or_create_user(user_id, {"afk": afk_data})

    def add_xp(self, user_id: int, xp: int) -> None:
        try:
            user = User.objects.raw({"user_id": str(user_id)}).first()
            user.xp += xp
            user.save()
        except DoesNotExist:
            self._update_or_create_user(user_id, {"xp": xp})

    def set_user_profile_photo(
        self,
        user_id: int,
        photo_url: Optional[str],
    ) -> None:
        self._update_or_create_user(user_id, {"profile_photo_url": photo_url})

    # ---Bot DB functions 
    def _get_bot(self) -> Bot:
        try:
            return Bot.objects.first()
        except DoesNotExist:
            bot = Bot()
            bot.save()
            return bot

    def enable_command(
        self,
        command_name: str,
        enabled: bool,
        reason: Optional[str] = None,
    ) -> None:
        bot = self._get_bot()

        for cmd in bot.commands:
            if cmd.get("command") == command_name:
                cmd.update({"enabled": enabled, "reason": reason})
                bot.save()
                return

        bot.commands.append(
            {"command": command_name, "enabled": enabled, "reason": reason}
        )
        bot.save()

    def get_cmd_info(self, command_name: str) -> Dict[str, Any]:
        bot = self._get_bot()

        for cmd in bot.commands:
            if cmd.get("command") == command_name:
                return cmd

        default = {"command": command_name, "enabled": True, "reason": None}
        bot.commands.append(default)
        bot.save()
        return default

    def add_sticker_sets(
        self,
        pack_name: str,
        pack_title: str,
        format: str,
        creator_user_id: int,
    ) -> bool:
        bot = self._get_bot()

        if any(s["pack_name"] == pack_name for s in bot.sticker_sets):
            return False

        bot.sticker_sets.append(
            {
                "pack_name": pack_name,
                "pack_title": pack_title,
                "format": format,
                "creator_user_id": creator_user_id,
            }
        )
        bot.save()
        return True

    def delete_sticker_set(self, pack_name: str) -> bool:
        bot = self._get_bot()

        for sticker in bot.sticker_sets:
            if sticker["pack_name"] == pack_name:
                bot.sticker_sets.remove(sticker)
                bot.save()
                return True

        return False

    def get_user_sticker_sets(self, user_id: int) -> List[Dict[str, Any]]:
        return [
            s
            for s in self._get_bot().sticker_sets
            if s.get("creator_user_id") == user_id
        ]

    def get_all_sticker_sets(self) -> List[Dict[str, Any]]:
        return self._get_bot().sticker_sets

