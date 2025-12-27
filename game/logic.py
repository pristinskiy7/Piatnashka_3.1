# game/logic.py
import random


def new_game(w, h, max_attempts=1000):
    """Создать новую решаемую раскладку.
    Если за max_attempts не удаётся найти решаемую — возвращаем None.
    """
    nums = list(range(w * h))  # плитки от 0 до w*h-1, где 0 = пустая
    attempts = 0

    while attempts < max_attempts:
        random.shuffle(nums)

        board = []
        idx = 0
        for y in range(h):
            row = []
            for x in range(w):
                row.append(nums[idx])
                idx += 1
            board.append(row)

        # проверяем решаемость
        if is_solvable(board, w, h):
            return board

        attempts += 1

    # если не удалось найти решаемую раскладку
    print(f"Не удалось создать решаемую раскладку за {max_attempts} попыток")
    return None


def find_zero(board):
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if val == 0:
                return x, y
    return None


def try_move(board, x, y):
    zx, zy = find_zero(board)

    if abs(zx - x) + abs(zy - y) != 1:
        return False

    board[zy][zx], board[y][x] = board[y][x], board[zy][zx]
    return True


def is_finished(board):
    """Проверка: поле собрано правильно"""
    h = len(board)
    w = len(board[0])

    expected = 1
    for y in range(h):
        for x in range(w):
            # последняя клетка должна быть пустой
            if y == h - 1 and x == w - 1:
                return board[y][x] == 0
            # все остальные клетки должны идти по порядку
            if board[y][x] != expected:
                return False
            expected += 1

    return True



def is_solvable(board, w, h):
    """Проверка решаемости раскладки."""
    tiles = []
    empty_y = None
    for y in range(h):
        for x in range(w):
            val = board[y][x]
            if val == 0:
                empty_y = y
            else:
                tiles.append(val)

    # считаем инверсии
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1

    # проверка по правилам
    if w % 2 == 1:
        # нечётная ширина → решаемо, если инверсий чётное число
        return inversions % 2 == 0
    else:
        # чётная ширина → учитываем строку пустой клетки от низа
        if empty_y is None:
            return False
        empty_row_from_bottom = h - empty_y
        return (inversions % 2 == 0) == (empty_row_from_bottom % 2 == 1)