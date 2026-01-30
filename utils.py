"""Модуль для реализации логики игры «Крестики-нолики» в Telegram-боте.

Содержит функции для инициализации игрового поля, обработки ходов игроков,
проверки победителя и генерации инлайн-клавиатуры для взаимодействия
c пользователем через Telegram.
"""
from copy import deepcopy
from typing import Literal

from telegram import InlineKeyboardButton

from constants import (
    CROSS,
    DEFAULT_STATE,
    FREE_SPACE,
    WIDTH,
    ZERO,
)


def get_default_state() -> list[list[str]]:
    """Возвращает копию начального состояния игрового поля.

    Используется для инициализации новой игры. Возвращается глубокая копия,
    чтобы избежать неожиданных изменений глобальной константы DEFAULT_STATE.

    Returns:
        list[list[str]]: Двумерный список, представляющий пустое игровое поле 3x3.

    """
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: list[list[str]]) -> list[list[InlineKeyboardButton]]:
    """Генерирует клавиатуру Telegram для отображения игрового поля крестики-нолики.

    Создаёт сетку из инлайн-кнопок размером 3x3, где каждая кнопка отображает
    текущее содержимое соответствующей ячейки поля и содержит callback_data
    в формате 'rc' (например, '01' для строки 0, столбца 1).

    Args:
        state (list[list[str]]): Текущее состояние игрового поля 3x3.

    Returns:
        list[list[InlineKeyboardButton]]: Двумерный список кнопок
        для отправки в Telegram.

    """
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f"{r}{c}")
            for c in range(WIDTH)
        ]
        for r in range(WIDTH)
    ]


def make_move(
    fields: list[list[str]],
    row: int,
    column: int,
    sign: Literal["X", "O"],
) -> bool:
    """Выполняет ход игрока на указанной позиции игрового поля.

    Проверяет корректность координат и доступность ячейки. Если ход допустим,
    обновляет поле указанным символом ('X' или 'O').

    Args:
        fields (list[list[str]]): Текущее состояние игрового поля.
        row (int): Индекс строки (0-2).
        column (int): Индекс столбца (0-2).
        sign (Literal["X", "O"]): Символ игрока — либо "X", либо "O".

    Returns:
        bool: True, если ход успешно выполнен; False, если ход недопустим
              (некорректные координаты или ячейка уже занята).

    """
    # Проверяем корректность хода
    if not (0 <= row < WIDTH and 0 <= column < WIDTH):
        return False
    if fields[row][column] != FREE_SPACE:
        return False

    # Делаем ход
    fields[row][column] = sign
    return True


def won(fields: list[list[str]]) -> Literal["X", "O"] | None:
    """Проверяет, выиграл ли один из игроков на текущем игровом поле.

    Анализирует все возможные выигрышные комбинации: три в ряд по горизонтали,
    вертикали и двум диагоналям.

    Args:
        fields (list[list[str]]): Текущее состояние игрового поля 3x3.

    Returns:
        Literal["X", "O"] | None: Символ победителя ("X" или "O"), если есть победитель;
                                  None, если победитель отсутствует.

    """
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
