from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from Models import User


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "removewarn",
                "aliases": ["unwarn"],
                "category": "Chat",
                "description": {
                    "content": "Remove warnings from a user.",
                    "usage": "<reply | @user> [all]",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        text: str = context.get("text", "") or ""
        remove_all: bool = "all" in text.split()

        users: list[User] = []
        if M.reply_to_user:
            users.append(M.reply_to_user)
        elif M.mentions:
            users.extend(M.mentions)

        if not users:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❗ <b>『Invalid Usage』</b>\n"
                    "└ <i>Reply to a user or mention them to remove warnings.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        for user in users:
            if user.user_id == self.client.bot.id:
                continue

            chat = self.client.db.get_group_by_chat_id(M.chat_id)
            warns: list[dict[str, Any]] = chat.warns or []

            entry = next(
                (w for w in warns if w.get("user_id") == user.user_id),
                None,
            )

            if not entry:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "ℹ️ <b>『No Warnings』</b>\n"
                        f"└ <i>{user.user_full_name} has no warnings.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                continue

            if remove_all:
                warns.remove(entry)

                self.client.db._update_or_create_group(
                    M.chat_id,
                    {"warns": warns},
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "<blockquote>"
                        "⚖️ <b>『Warnings Cleared』</b>\n"
                        f"├ <b>User:</b> {user.mention}\n"
                        f"├ <b>By:</b> {M.sender.mention}\n"
                        "└ <b>Status:</b> All warnings removed ✅"
                        "</blockquote>"
                    ),
                    parse_mode="HTML",
                    reply_to_message_id=M.message_id,
                )
                continue

            entry["count"] = max(entry.get("count", 0) - 1, 0)

            if entry.get("reasons"):
                entry["reasons"].pop()

            if entry["count"] == 0:
                warns.remove(entry)

            self.client.db._update_or_create_group(
                M.chat_id,
                {"warns": warns},
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "<blockquote>"
                    "⚖️ <b>『Warning Updated』</b>\n"
                    f"├ <b>User:</b> {user.mention}\n"
                    f"├ <b>By:</b> {M.sender.mention}\n"
                    f"└ <b>Warnings:</b> {entry.get('count', 0)}/3"
                    "</blockquote>"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )