from __future__ import annotations

from typing import Any, TYPE_CHECKING

from Libs import BaseCommand
from telegram.constants import ParseMode

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):
    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "help",
                "aliases": ["cmds", "commands"],
                "category": "general",
                "description": {
                    "content": "List all available commands and their usage.",
                    "usage": "[command_name]",
                },
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        try:
            cmd_arg: str = context.get("text", "").strip().lower()

            if cmd_arg:
                target = self.handler._commands.get(cmd_arg)
                if target:
                    desc = target.config.get("description", {})
                    content: str = desc.get("content", "No description available.")
                    usage: str = desc.get("usage", "")

                    text: str = (
                        "『<i>Command Info</i>』 📖\n"
                        f"├ <i>Command</i>: <code>{target.config.command}</code>\n"
                        f"├ <i>Category</i>: {target.config.get('category', 'None')}\n"
                        f"├ <i>Usage</i>: {self.client.prefix}{target.config.command} {usage}"
                        f"└ <i>Description</i>: {content}\n"
                    )

                    await self.client.bot.send_message(
                        chat_id=M.chat_id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=M.message_id,
                    )
                    return

            categories: dict[str, list[str]] = {}

            for cmd in self.handler._commands.values():
                category: str = cmd.config.get("category", "uncategorized").capitalize()
                categories.setdefault(category, []).append(
                    f"<code>{cmd.config.command}</code>"
                )

            text: str = "『<i>Available Commands</i>』 🛠️\n\n"

            for category, cmds in sorted(categories.items()):
                text += (
                    f"『<i>{category}</i>』\n"
                    f"└ {', '.join(sorted(cmds))}\n\n"
                )

            text += f"Use <code>{self.client.prefix}help [command]</code> for details."

            await self.client.bot.send_message(
                chat_id=M.chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=M.message_id,
            )

        except Exception as e:
            error: str = self.client.utils.format_execution_error(e=e, file_filter=__file__)
            await self.client.bot.send_message(chat_id=M.chat_id, text=error, reply_to_message_id=M.message_id, parse_mode="HTML",)