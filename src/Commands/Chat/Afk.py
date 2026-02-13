from __future__ import annotations
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

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
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

            error_text: str = (
                "『<i>Error</i>』⚠️\n"
                "└ <i>Status</i>: Something went wrong"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=error_text,
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )