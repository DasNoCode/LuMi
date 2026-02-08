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
        username: list[str] = context.get("text", [])
        if not username:
            await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ Please provide a GitHub username.",
                reply_to_message_id=M.message_id,
            )
            return

        data: dict[str, Any] = await self.client.utils.fetch(
            f"https://api.popcat.xyz/v2/github/{username}"
        )

        if data.get("error"):
            await self.client.send_message(
                chat_id=M.chat_id,
                text="❌ GitHub user not found.",
                reply_to_message_id=M.message_id,
            )
            return

        info: dict[str, Any] = data["message"]
        avatar_url: str = info["avatar"]

        text: str = (
            f'<a href="{avatar_url}">&#8204;</a>'
            "<blockquote>"
            "👨🏻‍💻 <b>GitHub Information:</b>\n"
            f"├ <b>Name:</b> {info['name']}\n"
            f"├ <b>Username:</b> {username}\n"
            f"├ <b>Account Type:</b> {info['account_type']}\n"
            f"├ <b>Public Repos:</b> {info['public_repos']}\n"
            f"├ <b>Followers:</b> {info['followers']}\n"
            f"├ <b>Following:</b> {info['following']}\n"
            f"├ <b>Location:</b> {info['location']}\n"
            f"└ <b>Bio:</b> {info['bio']}"
            "</blockquote>"
        )

        await self.client.send_message(
            chat_id=M.chat_id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )