from __future__ import annotations

import asyncio
import numpy as np
from typing import Any, TYPE_CHECKING, Tuple, Optional

from Libs import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

if TYPE_CHECKING:
    from Libs import SuperClient, Message
    from Handler import CommandHandler


class Command(BaseCommand):

    TURN_TIMEOUT: int = 60

    def __init__(self, client: SuperClient, handler: CommandHandler) -> None:
        super().__init__(
            client,
            handler,
            {
                "command": "ttt",
                "category": "games",
                "description": {
                    "content": "Play Tic Tac Toe.",
                    "usage": "<reply | @user>",
                },
                "OnlyChat": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:

        if M.is_callback:
            await self._handle_callback(M)
            return

        target = M.reply_to_user or (M.mentions[0] if M.mentions else None)
        if not target:
            return

        if M.sender.user_id == target.user_id:
            return await self.client.bot.send_message(
                chat_id=M.chat_id, text="You can't challenge youself!"
            )

        if any(
            isinstance(k, tuple) and k[0] == "ttt" and k[1] == M.chat_id
            for k in self.client.interaction_store
        ):
            return

        if any(
            isinstance(k, tuple)
            and k[0] == "ttt"
            and (M.sender.user_id in k or target.user_id in k)
            for k in self.client.interaction_store
        ):
            return

        pending_key = ("ttt_pending", M.chat_id)

        self.client.interaction_store[pending_key] = {
            "player1": M.sender.user_id,
            "player2": target.user_id,
            "player1_name": M.sender.mention,
            "player2_name": target.mention,
            "origin": M.message_id,
        }

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "『Accept』",
                        callback_data="cmd:ttt action:accept",
                    ),
                    InlineKeyboardButton(
                        "『Reject』",
                        callback_data="cmd:ttt action:reject",
                    ),
                ]
            ]
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="🎮 <b>『Tic Tac Toe Challenge』</b>\n└Accept or Reject.",
            parse_mode="HTML",
            reply_markup=keyboard,
            reply_to_message_id=M.message_id,
        )

    async def _handle_callback(self, M: Message) -> None:

        flags = dict(part.split(":") for part in M.message.split() if ":" in part)

        chat_id = M.chat_id

        if flags.get("action"):

            pending_key = ("ttt_pending", chat_id)
            pending = self.client.interaction_store.get(pending_key)
            if not pending:
                return

            if M.sender.user_id != pending["player2"]:
                await self.client.bot.answer_callback_query(
                    callback_query_id=M.callback_id,
                    text="This game isn't for you.",
                    show_alert=True,
                )
                return

            if flags["action"] == "reject":
                self.client.interaction_store.pop(pending_key, None)

                await self.client.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=M.message_id,
                    text="<b>『Challenge Rejected』</b>",
                    parse_mode="HTML",
                    reply_markup=None,
                )
                return

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "1 Round",
                            callback_data="cmd:ttt rounds:1",
                        ),
                        InlineKeyboardButton(
                            "2 Rounds",
                            callback_data="cmd:ttt rounds:2",
                        ),
                        InlineKeyboardButton(
                            "3 Rounds",
                            callback_data="cmd:ttt rounds:3",
                        ),
                    ]
                ]
            )

            await self.client.bot.edit_message_text(
                chat_id=chat_id,
                message_id=M.message_id,
                text="<b>『Select Rounds』</b>",
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return

        if "rounds" in flags:

            pending_key = ("ttt_pending", chat_id)
            pending = self.client.interaction_store.get(pending_key)
            if not pending:
                return

            rounds = int(flags["rounds"])
            rounds = 1 if rounds < 1 else 3 if rounds > 3 else rounds

            key = ("ttt", chat_id, pending["player1"], pending["player2"])

            board = np.zeros((3, 3), dtype=int)

            self.client.interaction_store[key] = {
                "board": board,
                "player1": pending["player1"],
                "player2": pending["player2"],
                "player1_name": pending["player1_name"],
                "player2_name": pending["player2_name"],
                "turn": pending["player1"],
                "rounds": rounds,
                "current_round": 1,
                "score1": 0,
                "score2": 0,
                "message_id": M.message_id,
                "turn_task": None,
            }

            self.client.interaction_store.pop(pending_key, None)

            await self._render(key)
            await self._start_timer(key)
            return

        if flags.get("defeat") == "true":

            key = next(
                (
                    k
                    for k in self.client.interaction_store
                    if isinstance(k, tuple)
                    and k[0] == "ttt"
                    and k[1] == chat_id
                    and M.sender.user_id in k
                ),
                None,
            )

            if not key:
                return

            await self._finish_game(key, defeated=M.sender.user_id)
            return

        if "r" not in flags or "c" not in flags:
            return

        key = next(
            (
                k
                for k in self.client.interaction_store
                if isinstance(k, tuple)
                and k[0] == "ttt"
                and k[1] == chat_id
                and M.sender.user_id in k
            ),
            None,
        )

        if not key:
            return

        game = self.client.interaction_store[key]

        if M.sender.user_id != game["turn"]:
            await self.client.bot.answer_callback_query(
                callback_query_id=M.callback_id,
                text="Not your turn.",
                show_alert=True,
            )
            return

        r, c = int(flags["r"]), int(flags["c"])

        if game["board"][r][c] != 0:
            await self.client.bot.answer_callback_query(
                callback_query_id=M.callback_id,
                text="Position already occupied.",
                show_alert=True,
            )
            return

        player_value = 1 if M.sender.user_id == game["player1"] else -1
        game["board"][r, c] = player_value

        winner = self.check_winner(game["board"])

        if winner is not None:
            await self._handle_round_win(key, winner)
            return

        game["turn"] = (
            game["player2"] if game["turn"] == game["player1"] else game["player1"]
        )

        await self._start_timer(key)
        await self._render(key)

    async def _handle_round_win(self, key: Tuple[Any, ...], winner: int) -> None:
        game = self.client.interaction_store[key]

        if winner == 1:
            game["score1"] += 1
        else:
            game["score2"] += 1

        game["current_round"] += 1

        if game["current_round"] > game["rounds"]:
            await self._finish_game(key)
            return

        game["board"] = np.zeros((3, 3), dtype=int)
        game["turn"] = game["player1"]

        await self._start_timer(key)
        await self._render(key)

    async def _render(self, key: Tuple[Any, ...]) -> None:
        game = self.client.interaction_store[key]

        buttons = []
        for r in range(3):
            row = []
            for c in range(3):
                val = game["board"][r][c]
                symbol = "❌" if val == 1 else "⭕" if val == -1 else " "
                row.append(
                    InlineKeyboardButton(
                        symbol,
                        callback_data=f"cmd:ttt r:{r} c:{c}",
                    )
                )
            buttons.append(row)

        buttons.append(
            [
                InlineKeyboardButton(
                    "🏳 Defeated",
                    callback_data="cmd:ttt defeat:true",
                )
            ]
        )

        text = (
            "🎮 <b>『Tic Tac Toe』</b>\n"
            f"├ Round: {game['current_round']}/{game['rounds']}\n"
            f"├ Score: {game['score1']} - {game['score2']}\n"
            f"└ Turn: {game['player2_name'] if game['player1']!= game['turn'] else game['player1_name']}"
        )

        await self.client.bot.edit_message_text(
            chat_id=key[1],
            message_id=game["message_id"],
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML",
        )

    async def _start_timer(self, key: Tuple[Any, ...]) -> None:
        game = self.client.interaction_store.get(key)
        if not game:
            return

        if game["turn_task"]:
            game["turn_task"].cancel()

        async def expire():
            await asyncio.sleep(self.TURN_TIMEOUT)
            if key not in self.client.interaction_store:
                return

            await self.client.bot.edit_message_text(
                chat_id=key[1],
                message_id=game["message_id"],
                text="⏰ <b>『Turn Expired』</b>",
                parse_mode="HTML",
                reply_markup=None,
            )

            self._cleanup(key)

        game["turn_task"] = asyncio.create_task(expire())

    async def _finish_game(
        self,
        key: Tuple[Any, ...],
        defeated: Optional[int] = None,
    ) -> None:

        game = self.client.interaction_store.get(key)
        if not game:
            return

        if defeated:

            winner = (
                game["player2_name"]
                if defeated == game["player1"]
                else game["player1_name"]
            )
            opponet = (
                game["player1_name"]
                if defeated == game["player1"]
                else game["player2_name"]
            )
            text = (
                "🏳 <b>『Surrender』</b>\n"
                f"├ Player {opponet} surrendered\n"
                f"└ Winner: {winner}"
            )

        else:

            text = (
                "🏆 <b>『Final Result』</b>\n"
                f"├ {game['player1_name']}: {game['score1']}\n"
                f"└ {game['player2_name']}: {game['score2']}"
            )

        await self.client.bot.edit_message_text(
            chat_id=key[1],
            message_id=game["message_id"],
            text=text,
            parse_mode="HTML",
            reply_markup=None,
        )

        self._cleanup(key)

    def _cleanup(self, key: Tuple[Any, ...]) -> None:
        game = self.client.interaction_store.get(key)
        if not game:
            return

        if game.get("turn_task"):
            game["turn_task"].cancel()

        self.client.interaction_store.pop(key, None)

    @staticmethod
    def check_winner(board) -> Optional[int]:
        sums = np.concatenate(
            (
                board.sum(axis=0),
                board.sum(axis=1),
                [np.trace(board)],
                [np.trace(np.fliplr(board))],
            )
        )

        if 3 in sums:
            return 1
        if -3 in sums:
            return -1
        return None
