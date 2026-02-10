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
                "command": "stickersets",
                "aliases": ["allsets", "sets"],
                "category": "sticker",
                "description": {
                    "content": "List all sticker sets created using this bot.",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        sets: list[dict[str, Any]] = self.client.db.get_all_sticker_sets()

        if not sets:
            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text="ℹ️ No sticker sets have been created yet.",
                reply_to_message_id=M.message_id,
            )
            return

        lines: list[str] = []

        for i, s in enumerate(sets, start=1):
            lines.append(
                "<blockquote>"
                f"├ <b>#{i}</b>\n"
                f"├ <b>Title:</b> {s.get('pack_title', 'N/A')}\n"
                f"├ <b>Name:</b> <code>{s.get('pack_name')}</code>\n"
                f"├ <b>Format:</b> {s.get('format')}\n"
                f"└ <b>Creator ID:</b> <code>{s.get('creator_user_id')}</code>"
                "</blockquote>"
            )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="\n".join(lines),
            parse_mode="HTML",
            reply_to_message_id=M.message_id,
        )