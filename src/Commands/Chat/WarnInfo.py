from __future__ import annotations

from typing import Any, TYPE_CHECKING
from Libs import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "warninfo",
                "aliases": ["warns"],
                "category": "moderation",
                "description": {
                    "content": "Show warned users in this chat.",
                    "usage": "<reply | @user>",
                },
                "OnlyChat": True,
                "OnlyAdmin": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        flags: dict[str, str] = context.get("flags", {})
        page: int = max(int(flags.get("page", "1")), 1)

        chat = self.client.db.get_group_by_chat_id(M.chat_id)
        warns: list[dict[str, Any]] = chat.warns or []

        target = M.reply_to_user or (M.mentioned[0] if M.mentioned else None)

        if target:
            entry = next(
                (w for w in warns if w["user_id"] == target.user_id),
                None,
            )

            if not entry:
                await self.client.bot.send_message(
                    chat_id=M.chat_id,
                    text=(
                        "ℹ️ <b>『No Warnings』</b>\n"
                        f"└ <i>{target.user_full_name} has no warnings.</i>"
                    ),
                    reply_to_message_id=M.message_id,
                    parse_mode="HTML",
                )
                return

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "<blockquote>"
                    "⚠️ <b>『User Warning Info』</b>\n"
                    f"├ <b>User:</b> {target.user_full_name}\n"
                    f"└ <b>Warnings:</b> {entry['count']}/3"
                    "</blockquote>"
                ),
                parse_mode="HTML",
                reply_to_message_id=M.message_id,
            )
            return

        if not warns:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=(
                    "ℹ️ <b>『No Warned Users』</b>\n"
                    "└ <i>No warned users in this chat.</i>"
                ),
                reply_to_message_id=M.message_id,
                parse_mode="HTML",
            )
            return

        per_page: int = 10
        total_pages: int = (len(warns) + per_page - 1) // per_page
        page = min(page, total_pages)

        start: int = (page - 1) * per_page
        end: int = start + per_page
        chunk = warns[start:end]

        lines: list[str] = []

        for i, w in enumerate(chunk):
            prefix: str = "└" if i == len(chunk) - 1 else "├"
            lines.append(
                f"{prefix} <a href=\"tg://user?id={w['user_id']}\">"
                f"{w['user_full_name']}</a> "
                f"— {w['count']}/3"
            )

        text: str = (
            "<blockquote>"
            "⚠️ <b>『Warned Users』</b>\n"
            + "\n".join(lines)
            + f"\n└ <b>Page:</b> {page}/{total_pages}"
            "</blockquote>"
        )

        buttons: list[list[InlineKeyboardButton]] = []

        if total_pages > 1:
            nav: list[InlineKeyboardButton] = []

            if page > 1:
                nav.append(
                    InlineKeyboardButton(
                        "‹",
                        callback_data=f"cmd:warninfo page:{page - 1}",
                    )
                )

            if page < total_pages:
                nav.append(
                    InlineKeyboardButton(
                        "›",
                        callback_data=f"cmd:warninfo page:{page + 1}",
                    )
                )

            if nav:
                buttons.append(nav)

        markup = InlineKeyboardMarkup(buttons) if buttons else None

        if M.is_callback:
            await self.client.bot.edit_message_text(
                chat_id=M.chat_id,
                message_id=M.message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup,
            )
        else:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup,
                reply_to_message_id=M.message_id,
            )