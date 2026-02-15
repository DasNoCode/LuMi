from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote_plus
from datetime import datetime, timezone

from Libs import BaseCommand

if TYPE_CHECKING:
    from Models import User
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "discord",
                "category": "fun",
                "description": {
                    "content": "Generate a Discord-style message sticker.",
                    "usage": "<text> or reply to text [color:#ffcc99]",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:

            sender_db: User = self.client.db.get_user_by_user_id(
                M.sender.user_id
            )

            if sender_db and sender_db.afk.get("status"):
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "『<i>AFK Status</i>』💤\n"
                        "└ <i>Status</i>: You are already AFK"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            raw_text: str = context.get("text", "").strip()

            reason: str = " ".join(
                word for word in raw_text.split()
                if not word.startswith("@")
            ).strip()

            self.client.db.set_user_afk(
                user_id=M.sender.user_id,
                status=True,
                reason=reason,
            )

            text: str = (
                "『<i>AFK Enabled</i>』💤\n"
                f"├ <i>User</i>: {M.sender.mention}\n"
                + (
                    f"└ <i>Reason</i>: {reason}"
                    if reason
                    else "└ <i>Reason</i>: No reason provided"
                )
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
        except Exception as e:

            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "『<i>Error</i>』⚠️\n"
                    "└ <i>Status</i>: Something went wrong"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )