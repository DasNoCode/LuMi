from __future__ import annotations
from typing import Any, TYPE_CHECKING
from Helpers.JsonObject import JsonObject

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class BaseCommand:
    def __init__(
        self,
        client: SuperClient,
        handler: CommandHandler,
        config: dict[str, Any],
    ) -> None:
        self.client: SuperClient = client
        self.handler: CommandHandler = handler
        self.config: JsonObject = JsonObject(config)

    async def exec(self, M: Message, context: dict[str, Any]) -> None:
        self.client.log.error(
            "[ERROR] [Exec] exec function must be declared in subclasses"
        )
