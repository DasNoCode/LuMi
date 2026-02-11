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
                "command": "bans",
                "aliases": ["banlist"],
                "category": "chat",
                "description": {
                    "content": "Show all banned users in this chat.",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        group = self.client.db.get_group_by_chat_id(M.chat_id)
        bans: list[dict[str, Any]] = getattr(group, "bans", []) or []

        if not bans:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "ℹ️ <b>『No Bans』</b>\n"
                    "└ <i>No users are banned in this chat.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        lines: list[str] = []

        for i, ban in enumerate(bans, start=1):
            user_id: int = ban.get("user_id")
            reason: str = ban.get("reason") or "No reason provided"
            by_id: int | None = ban.get("by_user_id")

            banner_name: str = "Unknown"
            if by_id:
                try:
                    user = await self.client.bot.get_chat(by_id)
                    banner_name = (
                        f"@{user.username}"
                        if getattr(user, "username", None)
                        else str(by_id)
                    )
                except Exception:
                    banner_name = str(by_id)

            prefix: str = "└" if i == len(bans) else "├"

            lines.append(
                f"{prefix} <b>#{i}</b>\n"
                f"   ├ <b>User ID:</b> <code>{user_id}</code>\n"
                f"   ├ <b>Reason:</b> {reason}\n"
                f"   └ <b>Banned By:</b> {banner_name}"
            )

        text: str = (
            "<blockquote>"
            "🚫 <b>『Banned Users』</b>\n"
            + "\n".join(lines) +
            "\n</blockquote>"
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )