from __future__ import annotations
import traceback
from typing import Any, TYPE_CHECKING
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
                "command": "afk",
                "category": "chat",
                "description": {
                    "content": (
                        "Set yourself as AFK (Away From Keyboard). "
                        "Mentions will auto-reply that you're unavailable "
                        "and notify you when you're mentioned."
                    ),
                },
                "OnlyChat": True,
            },
        )

    async def exec(self, M: Message, context: list[Any]) -> None:
        try:
            raw_text: str = context.get("text", "").strip()

            reason: str = " ".join(
                word for word in raw_text.split()
                if not word.startswith("@")
            )

            self.client.db.set_user_afk(
                user_id=M.sender.user_id,
                status=True,
                reason=reason,
            )

            afk_text: str = (
                "💤 <b>『AFK Enabled』</b>\n"
                f"├ <b>User:</b> @{M.sender.user_name or M.sender.user_full_name}\n"
                + (
                    f"└ <b>Reason:</b> {reason}"
                    if reason
                    else "└ <i>No reason provided.</i>"
                )
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=afk_text,
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
                    "⚠️ <b>『Error』</b>\n"
                    "└ <i>Something went wrong. Please try again later.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )