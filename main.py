#!/usr/bin/env python3

"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
import logging
import random
from copy import deepcopy
from config import (
    TOKEN,
    CONTINUE_GAME, FINISH_GAME,
    FREE_SPACE, CROSS, ZERO,
    HELP_TURN_MESSAGE, END_MESSAGE,
    DEFAULT_STATE,
    HEIGHT, WIDTH,
)
from dotenv import load_dotenv
from functools import wraps
from typing import Literal

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


# Загружает переменные из .env в окружение
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: list[list[str]]) -> list[list[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f"{r}{c}")
            for c in range(WIDTH)
        ]
        for r in range(HEIGHT)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data["keyboard_state"] = get_default_state()
    keyboard = generate_keyboard(context.user_data["keyboard_state"])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(HELP_TURN_MESSAGE.format(sign=CROSS),
                                    reply_markup=reply_markup)
    return CONTINUE_GAME


def update_keyboard(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await func(update, context)

        query = update.callback_query
        fields = context.user_data["keyboard_state"]

        # Обновляем сообщение-подсказку
        if result == CONTINUE_GAME:
            await query.edit_message_text(text=HELP_TURN_MESSAGE.format(sign=CROSS))
        elif result == FINISH_GAME:
            await query.edit_message_text(text=END_MESSAGE.format(sign=won(fields)))

        # Обновляем клавиатуру
        keyboard = generate_keyboard(fields)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

        return result

    return wrapper


@update_keyboard
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Main processing of the game"""
    fields = context.user_data["keyboard_state"]

    # Получаем ход первого игрока (CROSS)
    query = update.callback_query
    callback_data = query.data

    row, col = map(int, callback_data)

    # Если первый игрок делает некорректный ход, то продолжаем игру
    if not make_move(fields, row, col, CROSS):
        return CONTINUE_GAME

    # Если первый игрок делает победный ход, то завершаем игру
    if won(fields):
        return FINISH_GAME

    # Получаем ход второго игрока (ZERO)
    free_fields = [
        (r, c)
        for r in range(HEIGHT)
        for c in range(WIDTH)
        if fields[r][c] == FREE_SPACE
    ]

    row, col = random.choice(free_fields)

    # Второй игрок всегда делает корректный ход
    make_move(fields, row, col, ZERO)

    # Если второй игрок делает победный ход, то завершаем игру
    if won(fields):
        return FINISH_GAME

    return CONTINUE_GAME


def make_move(
    fields: list[str],
    row: int,
    column: int,
    sign: Literal[CROSS, ZERO]
) -> bool:
    # Проверяем корректность хода
    if not (0 <= row < HEIGHT and 0 <= column < WIDTH):
        return False
    if fields[row][column] != FREE_SPACE:
        return False

    # Делаем ход
    fields[row][column] = sign
    return True


def won(fields: list[str]) -> Literal[CROSS, ZERO] | None:
    """Check if crosses or zeros have won the game"""
    for sign in [CROSS, ZERO]:
        won_state = [sign] * 3
        # Проверяем строки
        for row_index in range(3):
            row = fields[row_index]
            if row == won_state:
                return sign

        # Проверяем столбцы
        for col_index in range(3):
            col = [
                fields[row_index][col_index]
                for row_index in range(3)
            ]
            if col == won_state:
                return sign

        # Проверяем главную диагональ
        diag = [
            fields[i][i]
            for i in range(3)
        ]
        if diag == won_state:
            return sign

        # Проверяем побочную диагональ
        side_diag = [
            fields[i][2 - i]
            for i in range(3)
        ]
        if side_diag == won_state:
            return sign

    return None


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """

    # reset state to default so you can play again with /start
    context.user_data["keyboard_state"] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot"s token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow "ABC"
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
