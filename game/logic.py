# game/logic.py

import random
from game.state import get_state, set_state


# --- 1. СИСТЕМА РАНГОВ И XP ---

def get_rank_info(total_xp):
    """Рассчитывает уровень и звание на основе общего XP."""
    xp_per_level = 1000
    level = (total_xp // xp_per_level) + 1
    xp_in_level = total_xp % xp_per_level
    progress = xp_in_level / xp_per_level

    ranks = ["Новичок", "Ученик", "Игрок", "Мастер", "Эксперт", "Гроссмейстер", "Легенда"]
    rank_idx = min((level - 1) // 5, len(ranks) - 1)

    return level, xp_in_level, xp_per_level, progress, ranks[rank_idx]


def calculate_current_xp():
    """Прогноз XP за текущую партию на основе точности и времени."""
    state = get_state()
    md_initial = max(state.get('md_initial', 1), 1)
    moves = max(state.get('moves_count', 0), 1)
    time_spent = max(state.get('time_elapsed', 0.0), 1.0)
    w, h = state.get('board_w', 3), state.get('board_h', 3)

    area_multiplier = (w * h) / 10.0
    xp_base = md_initial * area_multiplier

    k_accuracy = md_initial / moves
    k_speed = (md_initial * 2) / time_spent
    k_total = max(0.5, min(5.0, k_accuracy * k_speed))

    return round(xp_base * k_total)


# --- 2. ПРОВЕРКИ ---

def is_solved(state):
    """Проверяет, собрана ли головоломка."""
    tiles = state.get('tiles', [])
    w, h = state.get('board_w', 0), state.get('board_h', 0)
    if not tiles or w == 0: return False

    expected = 1
    for r in range(h):
        for c in range(w):
            val = tiles[r][c]
            if r == h - 1 and c == w - 1:
                return val == 0
            if val != expected:
                return False
            expected += 1
    return True


def is_tile_in_place(tile_value, row, col, board_w, board_h):
    """Нужна для подсветки плиток, стоящих на верном месте."""
    if tile_value == 0:
        return row == board_h - 1 and col == board_w - 1
    return tile_value == (row * board_w) + col + 1


# --- 3. КЛАССИЧЕСКОЕ ПЕРЕМЕШИВАНИЕ (БРУТФОРС + МАТЕМАТИКА) ---

def is_solvable(board_w, board_h, flat_tiles):
    """
    Математический фильтр решаемости.
    Для нечетной ширины: количество инверсий должно быть четным.
    Для четной ширины: сумма (инверсии + ряд пустой клетки от низа) определяет решаемость.
    """
    inversions = 0
    nums = [t for t in flat_tiles if t != 0]
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inversions += 1

    empty_idx = flat_tiles.index(0)
    empty_row_from_top = empty_idx // board_w
    # Номер строки с нуля, считая снизу (1 — последняя строка)
    row_from_bottom = board_h - empty_row_from_top

    if board_w % 2 != 0:
        return inversions % 2 == 0
    else:
        # Для четной ширины: если ряд от низа четный, инверсии должны быть нечетными (и наоборот)
        if row_from_bottom % 2 == 0:
            return inversions % 2 != 0
        else:
            return inversions % 2 == 0


def shuffle_board():
    """Полная случайная генерация раскладки."""
    state = get_state()
    w, h = state['board_w'], state['board_h']
    total_cells = w * h

    is_ok = False
    flat_tiles = []

    # Ищем решаемую комбинацию
    while not is_ok:
        temp_list = list(range(1, total_cells))
        random.shuffle(temp_list)
        temp_list.append(0)
        random.shuffle(temp_list)  # Случайное положение нуля

        if is_solvable(w, h, temp_list):
            flat_tiles = temp_list
            is_ok = True

    new_board = [flat_tiles[i * w: (i + 1) * w] for i in range(h)]

    # Считаем MD (Манхэттенское расстояние) для экономики
    total_md = 0
    for r in range(h):
        for c in range(w):
            v = new_board[r][c]
            if v != 0:
                tr, tc = (v - 1) // w, (v - 1) % w
                total_md += abs(r - tr) + abs(c - tc)

    set_state('tiles', new_board)
    set_state('md_initial', total_md)
    set_state('moves_count', 0)
    set_state('time_elapsed', 0.0)
    set_state('is_playing', True)
    print(f"ЛОГ: Случайное поле {w}x{h} создано. MD: {total_md}")


# --- 4. ХОДЫ ---

def make_move(tile_row, tile_col):
    """Механика перемещения плиток (поддерживает сдвиг целого ряда/столбца)."""
    state = get_state()
    if not state.get('is_playing'): return

    tiles = state['tiles']
    w, h = state['board_w'], state['board_h']

    # Ищем пустую клетку
    er, ec = -1, -1
    for r in range(h):
        for c in range(w):
            if tiles[r][c] == 0:
                er, ec = r, c;
                break

    move_made = False
    if tile_row == er:  # Горизонтальный сдвиг
        step = 1 if tile_col < ec else -1
        for c in range(ec, tile_col, -step):
            tiles[tile_row][c] = tiles[tile_row][c - step]
        move_made = True
    elif tile_col == ec:  # Вертикальный сдвиг
        step = 1 if tile_row < er else -1
        for r in range(er, tile_row, -step):
            tiles[r][tile_col] = tiles[r - step][tile_col]
        move_made = True

    if move_made:
        tiles[tile_row][tile_col] = 0
        set_state('moves_count', state['moves_count'] + 1)

        if is_solved(state):
            earned = calculate_current_xp()
            new_total = state.get('total_xp', 0) + earned
            set_state('total_xp', new_total)
            _, _, _, _, new_rank = get_rank_info(new_total)
            set_state('rank_title', new_rank)
            set_state('is_playing', False)