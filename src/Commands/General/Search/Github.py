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
                "command": "github",
                "category": "general",
                "description": {
                    "content": "Fetch GitHub profile information.",
                    "usage": "<username>",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        username: str = (context.get("text", "") or "").strip()

        if not username:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❗ <b>『Missing Username』</b>\n"
                    "└ <i>Please provide a GitHub username.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        data: dict[str, Any] = await self.client.utils.fetch(
            f"https://api.popcat.xyz/v2/github/{username}"
        )

        if data.get("error"):
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "❌ <b>『User Not Found』</b>\n"
                    "└ <i>GitHub user does not exist.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        info: dict[str, Any] = data["message"]
        avatar_url: str = info.get("avatar")

        text: str = (
            f'<a href="{avatar_url}">&#8204;</a>'
            "<blockquote>"
            "👨🏻‍💻 <b>『GitHub Information』</b>\n"
            f"├ <b>Name:</b> {info.get('name') or '—'}\n"
            f"├ <b>Username:</b> {username}\n"
            f"├ <b>Account Type:</b> {info.get('account_type') or '—'}\n"
            f"├ <b>Public Repos:</b> {info.get('public_repos', 0)}\n"
            f"├ <b>Followers:</b> {info.get('followers', 0)}\n"
            f"├ <b>Following:</b> {info.get('following', 0)}\n"
            f"├ <b>Location:</b> {info.get('location') or '—'}\n"
            f"└ <b>Bio:</b> {info.get('bio') or '—'}"
            "</blockquote>"
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )