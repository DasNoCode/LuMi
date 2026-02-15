from __future__ import annotations

import asyncio
import random
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
                "command": "tttbot",
                "category": "Game",
                "description": {
                    "content": "Play Tic Tac Toe against the bot.",
                },
                "OnlyChat": True,
            },
        )

    async def exec(self, M: Message, context: dict[str, Any]) -> None:

        if M.is_callback:
            await self._handle_callback(M)
            return

        if any(
            isinstance(k, tuple) and k[0] == "tttbot" and k[1] == M.chat_id
            for k in self.client.interaction_store
        ):
            return

        if any(
            isinstance(k, tuple) and k[0] in ("ttt", "tttbot") and M.sender.user_id in k
            for k in self.client.interaction_store
        ):
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "『1』 ", callback_data="cmd:tttbot rounds:1"
                    ),
                    InlineKeyboardButton(
                        "『2』", callback_data="cmd:tttbot rounds:2"
                    ),
                    InlineKeyboardButton(
                        "『3』", callback_data="cmd:tttbot rounds:3"
                    ),
                ]
            ]
        )

        await self.client.bot.send_message(
            chat_id=M.chat_id,
            text="『<i>Select Rounds</i>』 🎮 ",
            parse_mode="HTML",
            reply_markup=keyboard,
            reply_to_message_id=M.message_id,
        )

    async def _handle_callback(self, M: Message) -> None:

        flags = dict(part.split(":") for part in M.message.split() if ":" in part)

        if "rounds" in flags:

            rounds = int(flags["rounds"])
            rounds = 1 if rounds < 1 else 3 if rounds > 3 else rounds

            key = ("tttbot", M.chat_id, M.sender.user_id)

            board = np.zeros((3, 3), dtype=int)

            self.client.interaction_store[key] = {
                "board": board,
                "player": M.sender.user_id,
                "rounds": rounds,
                "current_round": 1,
                "score_user": 0,
                "score_bot": 0,
                "message_id": M.message_id,
                "turn_task": None,
            }

            await self._render(key)
            await self._start_timer(key)
            return

        key = next(
            (
                k
                for k in self.client.interaction_store
                if isinstance(k, tuple)
                and k[0] == "tttbot"
                and k[1] == M.chat_id
                and M.sender.user_id in k
            ),
            None,
        )

        if not key:
            return

        game = self.client.interaction_store[key]

        if flags.get("defeat") == "true":
            await self._finish_game(key, defeated=True)
            return

        if "r" not in flags or "c" not in flags:
            return

        r, c = int(flags["r"]), int(flags["c"])

        if game["board"][r][c] != 0:
            text = (
                "『Invalid Move』 ❌\n"
                "└ Position already occupied"
            )
            await self.client.bot.answer_callback_query(
                callback_query_id=M.callback_id,
                text=text,
                show_alert=True,
            )
            return

        game["board"][r, c] = -1

        winner = self.check_winner(game["board"])

        if winner is not None:
            await self._handle_round_win(key, winner)
            return

        if not np.any(game["board"] == 0):
            await self._handle_draw(key)
            return

        br, bc = self.bot_move(game["board"])
        game["board"][br, bc] = 1

        winner = self.check_winner(game["board"])

        if winner is not None:
            await self._handle_round_win(key, winner)
            return

        if not np.any(game["board"] == 0):
            await self._handle_draw(key)
            return

        await self._start_timer(key)
        await self._render(key)

    async def _handle_draw(self, key: Tuple[Any, ...]) -> None:

        game = self.client.interaction_store[key]
        game["current_round"] += 1

        if game["current_round"] > game["rounds"]:
            await self._finish_game(key)
            return

        game["board"] = np.zeros((3, 3), dtype=int)
        await self._render(key)

    async def _handle_round_win(self, key: Tuple[Any, ...], winner: int) -> None:

        game = self.client.interaction_store[key]

        if winner == 1:
            game["score_bot"] += 1
        else:
            game["score_user"] += 1

        game["current_round"] += 1

        if game["current_round"] > game["rounds"]:
            await self._finish_game(key)
            return

        game["board"] = np.zeros((3, 3), dtype=int)
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
                        callback_data=f"cmd:tttbot r:{r} c:{c}",
                    )
                )
            buttons.append(row)

        buttons.append(
            [InlineKeyboardButton("『Defeated』", callback_data="cmd:tttbot defeat:true")]
        )

        text = (
            "『<i>Tic Tac Toe vs Bot</i>』 🎮 \n"
            f"├ <i>Round</i>: {game['current_round']}/{game['rounds']}\n"
            f"├ <i>Score</i>: You {game['score_user']} - {game['score_bot']} Bot\n"
            "└ You are ⭕ | Bot is ❌"
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
            await self._finish_game(key)

        game["turn_task"] = asyncio.create_task(expire())

    async def _finish_game(self, key: Tuple[Any, ...], defeated: bool = False) -> None:
        game = self.client.interaction_store.get(key)
        if not game:
            return
    
        player_id: int = game["player"]
        db_user = self.client.db.get_user_by_user_id(player_id)
        current_xp: int = db_user.xp if db_user else 0
    
        xp_change: int = 0
    
        if defeated:
            loss: int = min(random.randint(1, 3), current_xp)
            if loss > 0:
                self.client.db.add_xp(user_id=player_id, xp=-loss)
            xp_change = -loss
    
            result = (
                "『<i>Surrender</i>』 🏳 \n"
                f"└ You lost {loss} XP"
            )
    
        else:
            is_player_winner: bool = game["score_user"] > game["score_bot"]
    
            if is_player_winner:
                gain: int = random.randint(1, 3)
                self.client.db.add_xp(user_id=player_id, xp=gain)
                xp_change = gain
            else:
                loss: int = min(random.randint(1, 3), current_xp)
                if loss > 0:
                    self.client.db.add_xp(user_id=player_id, xp=-loss)
                xp_change = -loss
    
            result = (
                "『<i>Final Result</i>』 🏆 \n"
                f"├ <i>You</i>: {game['score_user']}\n"
                f"├ <i>Bot</i>: {game['score_bot']}\n"
                f"└ <i>XP</i>: {'+' if xp_change > 0 else ''}{xp_change}"
            )

        await self.client.bot.edit_message_text(
            chat_id=key[1],
            message_id=game["message_id"],
            text=result,
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

    @staticmethod
    def bot_move(board):
        for i in range(3):
            row = board[i]
            if row.sum() == 2 or row.sum() == -2:
                j = np.where(row == 0)[0]
                if j.size:
                    return i, int(j[0])

        for j in range(3):
            col = board[:, j]
            if col.sum() == 2 or col.sum() == -2:
                i = np.where(col == 0)[0]
                if i.size:
                    return int(i[0]), j

        diag = np.diag(board)
        if diag.sum() == 2 or diag.sum() == -2:
            i = np.where(diag == 0)[0]
            if i.size:
                return int(i[0]), int(i[0])

        anti = np.diag(np.fliplr(board))
        if anti.sum() == 2 or anti.sum() == -2:
            i = np.where(anti == 0)[0]
            if i.size:
                return int(i[0]), int(2 - i[0])

        if board[1, 1] == 0:
            return 1, 1

        for r, c in ((0, 0), (0, 2), (2, 0), (2, 2)):
            if board[r, c] == 0:
                return r, c

        empty = np.argwhere(board == 0)
        if empty.size == 0:
            return 0, 0
        r, c = empty[0]
        return int(r), int(c)
