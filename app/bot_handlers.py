import random
from collections.abc import Callable
from functools import wraps

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from constants import (
    CONTINUE_GAME,
    CROSS,
    END_MESSAGE,
    FINISH_GAME,
    FREE_SPACE,
    HELP_TURN_MESSAGE,
    WIDTH,
    ZERO,
)
from app.game import generate_keyboard, get_default_state, make_move, won


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data["keyboard_state"] = get_default_state()
    keyboard = generate_keyboard(context.user_data["keyboard_state"])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(HELP_TURN_MESSAGE.format(sign=CROSS),
                                    reply_markup=reply_markup)
    return CONTINUE_GAME


def update_keyboard(
    func: Callable[[Update, ContextTypes.DEFAULT_TYPE], int],
) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], int]:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    """Main processing of the game."""
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
        for r in range(WIDTH)
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


async def end(_update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # reset state to default so you can play again with /start
    context.user_data["keyboard_state"] = get_default_state()
    return ConversationHandler.END
