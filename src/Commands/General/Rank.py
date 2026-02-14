from __future__ import annotations

import traceback
from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from Helpers import get_rank


if TYPE_CHECKING:
    from telegram import User, Message
    from Libs import SuperClient
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "rank",
                "category": "general",
                "description": {
                    "content": "Show the rank of a user based on XP.",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            users: list[User] = []

            flags: dict[str, Any] = context.get("flags", {})
            caption: str | None = flags.get("caption")

            if M.reply_to_user:
                users.append(M.reply_to_user)
            elif M.mentions:
                users.extend(M.mentions)
            else:
                users.append(M.sender)

            for user in users:
                db_user = self.client.db.get_user_by_user_id(
                    user.user_id
                )
                xp: int = db_user.xp if db_user else 0

                rank_data: dict[str, Any] = get_rank(xp)

                level: int = rank_data["level"]
                rank_name: str = rank_data["rank_name"]
                rank_emoji: str = rank_data["rank_emoji"]
                next_rank_name: str = rank_data["next_rank_name"]
                next_rank_emoji: str = rank_data["next_rank_emoji"]
                current_xp: int = rank_data["xp"]
                level_xp_target: int = rank_data["level_xp_target"]

                previous_level_xp: int = (
                    5 * ((level - 1) ** 2) + 50
                    if level > 1
                    else 0
                )

                avatar_url: str | None = (
                    await self.client.db.profile_to_url(
                        user_id=user.user_id
                    )
                )

                card_url: str = self.client.utils.rank_card(
                    user.mention,
                    avatar_url,
                    level,
                    current_xp,
                    level_xp_target,
                    previous_level_xp,
                )

                xp_needed: int = level_xp_target - current_xp

                text: str = (
                    f'<a href="{card_url}">&#8204;</a>'
                    "『<i>User Rank</i>』🏆\n"
                    f"├ <i>User</i>: {user.mention}\n"
                    f"├ <i>Rank</i>: {rank_name} {rank_emoji}\n"
                    f"├ <i>Next Rank</i>: {next_rank_name} {next_rank_emoji}\n"
                    f"└ <i>XP Needed</i>: {xp_needed}"
                    + (f"\n\n{caption}" if caption else "")
                )

                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=text,
                    parse_mode="HTML",
                    reply_to_message_id=M.message_id,
                )

        except Exception as e:
            self.client.log.error(
                f"[ERROR] {e.__traceback__.tb_lineno}: {e}"
            )