import sys
from copy import deepcopy
from unittest.mock import MagicMock
from typing import Literal

import pytest

# Мокируем модуль telegram до импорта модуля
sys.modules["telegram"] = MagicMock()
sys.modules["telegram.inline"] = MagicMock()
sys.modules["telegram.inline.inlinekeyboardbutton"] = MagicMock()

from constants import CROSS, ZERO, FREE_SPACE, WIDTH, DEFAULT_STATE
from utils import get_default_state, make_move, won

class TestGetDefaultState:
    """Тесты для функции get_default_state."""

    def test_returns_correct_structure(self):
        """Проверка структуры возвращаемого поля."""
        state = get_default_state()
        assert len(state) == WIDTH
        assert all(len(row) == WIDTH for row in state)
        assert all(cell == FREE_SPACE for row in state for cell in row)

    def test_returns_deep_copy(self):
        """Проверка, что возвращается глубокая копия (не ссылка на константу)."""
        state = get_default_state()
        state[0][0] = CROSS
        # Оригинальная константа не должна измениться
        assert DEFAULT_STATE[0][0] == FREE_SPACE
        assert get_default_state()[0][0] == FREE_SPACE

class TestMakeMove:
    """Тесты для функции make_move."""

    @pytest.fixture
    def empty_board(self) -> list[list[str]]:
        return get_default_state()

    def test_valid_move_returns_true(self, empty_board):
        """Корректный ход возвращает True и изменяет поле."""
        result = make_move(empty_board, 1, 1, CROSS)
        assert result is True
        assert empty_board[1][1] == CROSS

    def test_valid_move_with_zero(self, empty_board):
        """Корректный ход ноликом."""
        result = make_move(empty_board, 0, 2, ZERO)
        assert result is True
        assert empty_board[0][2] == ZERO

    @pytest.mark.parametrize("row,col", [
        (-1, 0), (3, 0), (0, -1), (0, 3), (5, 5), (-5, -5)
    ])
    def test_invalid_coordinates_return_false(self, empty_board, row, col):
        """Некорректные координаты возвращают False."""
        result = make_move(empty_board, row, col, CROSS)
        assert result is False
        assert empty_board == get_default_state()  # Поле не изменилось

    def test_occupied_cell_returns_false(self, empty_board):
        """Ход в занятую ячейку возвращает False."""
        make_move(empty_board, 0, 0, CROSS)  # Занимаем ячейку
        result = make_move(empty_board, 0, 0, ZERO)
        assert result is False
        assert empty_board[0][0] == CROSS  # Ячейка не перезаписана

    def test_board_not_mutated_on_invalid_move(self, empty_board):
        """Поле не изменяется при некорректном ходе."""
        original = deepcopy(empty_board)
        make_move(empty_board, 10, 10, CROSS)
        assert empty_board == original

class TestWon:
    """Тесты для функции won."""

    def test_empty_board_no_winner(self):
        """На пустом поле нет победителя."""
        assert won(get_default_state()) is None

    def test_no_winner_in_progress(self):
        """Позиция без победителя."""
        board = get_default_state()
        board[0][0] = CROSS
        board[1][1] = ZERO
        board[2][2] = CROSS
        assert won(board) is None

    @pytest.mark.parametrize("sign", [CROSS, ZERO])
    def test_winner_by_rows(self, sign: Literal["X", "O"]):
        """Победа по строкам для любого знака."""
        for row_idx in range(WIDTH):
            board = get_default_state()
            board[row_idx] = [sign] * WIDTH
            assert won(board) == sign

    @pytest.mark.parametrize("sign", [CROSS, ZERO])
    def test_winner_by_columns(self, sign: Literal["X", "O"]):
        """Победа по столбцам для любого знака."""
        for col_idx in range(WIDTH):
            board = get_default_state()
            for row_idx in range(WIDTH):
                board[row_idx][col_idx] = sign
            assert won(board) == sign

    @pytest.mark.parametrize("sign", [CROSS, ZERO])
    def test_winner_by_main_diagonal(self, sign: Literal["X", "O"]):
        """Победа по главной диагонали."""
        board = get_default_state()
        for i in range(WIDTH):
            board[i][i] = sign
        assert won(board) == sign

    @pytest.mark.parametrize("sign", [CROSS, ZERO])
    def test_winner_by_anti_diagonal(self, sign: Literal["X", "O"]):
        """Победа по побочной диагонали."""
        board = get_default_state()
        for i in range(WIDTH):
            board[i][WIDTH - 1 - i] = sign
        assert won(board) == sign

    def test_multiple_winners_not_possible(self):
        """На корректном поле не может быть двух победителей одновременно."""
        # Создаём невозможную позицию (только для проверки логики функции)
        board = get_default_state()
        board[0] = [CROSS] * WIDTH
        board[1] = [ZERO] * WIDTH
        # Функция вернёт первого найденного победителя (CROSS)
        assert won(board) == CROSS

    def test_partial_win_not_detected(self):
        """Две подряд идущие фигуры не считаются победой."""
        board = get_default_state()
        board[0][0] = CROSS
        board[0][1] = CROSS
        assert won(board) is None
