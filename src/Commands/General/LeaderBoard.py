from __future__ import annotations

from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from Helpers import get_rank

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler



class Command(BaseCommand):

    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "leaderboard",
                "aliases": ["top", "lb"],
                "category": "general",
                "description": {
                    "content": "Show the top 10 users with the highest XP.",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            from Models import User as UserModel

            top_users = list(
                UserModel.objects.all()
                .order_by([("xp", -1)])
                .limit(10)
            )

            if not top_users:
                return await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "『<i>No Data</i>』 ℹ️\n"
                        "└ No user data found in database"
                    ),
                    reply_to_message_id=M.message_id,
                )

            lines: list[str] = [
                "『<i>XP Leaderboard</i>』 🏆"
            ]

            for i, user_data in enumerate(top_users, 1):
                rank_info = get_rank(user_data.xp)

                medal = (
                    "🥇" if i == 1 else
                    "🥈" if i == 2 else
                    "🥉" if i == 3 else
                    "👤"
                )

                lines.append(
                    f"├ {medal} #{i} — {user_data.user_id}\n"
                    f"│   XP: {user_data.xp}\n"
                    f"│   Rank: {rank_info['rank_emoji']} {rank_info['rank_name']}"
                )

            lines.append(
                f"└ Use {self.client.prefix}rank to check your standing"
            )

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="\n".join(lines),
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
                    "『<i>Execution Error</i>』 ⚠️\n"
                    "└ Failed to load leaderboard"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )