# game/logic.py

import random
from game.state import get_state, set_state




def is_solved(state):
    """
    Проверяет, выиграна ли игра: все плитки на своих местах и 0 в правом нижнем углу.
    """
    tiles = state['tiles']
    board_w = state['board_w']
    board_h = state['board_h']

    for r in range(board_h):
        for c in range(board_w):
            tile_value = tiles[r][c]

            # Используем уже существующую логику is_tile_in_place для каждой ячейки
            if not is_tile_in_place(tile_value, r, c, board_w, board_h):
                return False  # Найдена хотя бы одна плитка не на месте

    return True  # Все плитки (и пустая) на месте

def get_inversions_count(flat_tiles):
    """Считает количество инверсий в линеаризованном списке плиток (исключая 0)."""
    count = 0
    # Создаем список, исключая пустую плитку (0)
    tiles_without_zero = [t for t in flat_tiles if t != 0]
    n = len(tiles_without_zero)

    for i in range(n):
        for j in range(i + 1, n):
            if tiles_without_zero[i] > tiles_without_zero[j]:
                count += 1
    return count


def get_target_pos(tile_value, board_w, board_h):
    """
    Повертає цільову (фінальну) позицію (r, c) для даної плитки.
    Пуста плитка (0) знаходиться в правому нижньому куті.
    """
    if tile_value == 0:
        target_index = board_w * board_h - 1
    else:
        target_index = tile_value - 1

    target_r = target_index // board_w
    target_c = target_index % board_w
    return target_r, target_c


def calculate_initial_S(tiles, board_w, board_h):
    """
    Рассчитывает початкову складність (S) на основі суми Манхеттенської відстані
    та кількості інверсій (з вагою 3). S використовується як нормалізаційний фактор.
    """
    manhattan_distance_sum = 0
    flat_tiles = []

    for r in range(board_h):
        for c in range(board_w):
            tile_value = tiles[r][c]
            flat_tiles.append(tile_value)

            if tile_value != 0:
                target_r, target_c = get_target_pos(tile_value, board_w, board_h)

                # Манхеттенська відстань: |поточний r - цільовий r| + |поточний c - цільовий c|
                distance = abs(r - target_r) + abs(c - target_c)
                manhattan_distance_sum += distance

    # Використовуємо існуючу функцію для інверсій
    inversions_count = get_inversions_count(flat_tiles)

    # Формула складності: S = Manhattan + 3 * Inversions
    S_initial = manhattan_distance_sum + 3 * inversions_count

    return max(1, S_initial)  # Запобігаємо діленню на нуль



def is_solvable(board_w, board_h, flat_tiles):
    """ Проверяет решаемость головоломки N-Puzzle (Пятнашки)."""

    # 1. Считаем количество инверсий
    inv_count = get_inversions_count(flat_tiles)

    # 2. Находим ряд пустой ячейки (счет с НИЖНЕГО края)
    empty_index = flat_tiles.index(0)  # Индекс 0 в линеаризованном списке
    empty_row_from_top = empty_index // board_w  # Ряд с верхнего края (0, 1, 2...)
    empty_row_from_bottom = board_h - empty_row_from_top  # Ряд с нижнего края (1, 2, 3...)

    # 3. Применяем правила решаемости

    # A. Если ширина поля (W) нечетна
    if board_w % 2 != 0:
        # Решаемо, если количество инверсий четно
        return inv_count % 2 == 0

    # B. Если ширина поля (W) четна
    else:
        # Инверсии ЧЕТНО И ряд 0 НЕЧЕТНЫЙ (1, 3, 5...)
        if inv_count % 2 == 0:
            return empty_row_from_bottom % 2 != 0

        # Инверсии НЕЧЕТНО И ряд 0 ЧЕТНЫЙ (2, 4, 6...)
        else:
            return empty_row_from_bottom % 2 == 0


def is_tile_in_place(tile_value, row, col, board_w, board_h):
    """
    Проверяет, стоит ли плитка на своем конечном месте в упорядоченном поле.
    Пустая ячейка (0) считается "на своем месте", только если она в самом конце.
    """

    # 1. Рассчитываем идеальное значение для данной позиции (row, col)
    # Формула: (row * board_w) + col + 1

    expected_value = (row * board_w) + col + 1

    # 2. Проверка для числовых плиток (1, 2, 3...)
    if tile_value != 0:
        return tile_value == expected_value

    # 3. Проверка для пустой ячейки (0)
    else:
        # Пустая ячейка должна быть в правом нижнем углу
        is_last_position = (row == board_h - 1) and (col == board_w - 1)
        return is_last_position


def shuffle_board():
    """
    Перемешивает плитки, гарантируя решаемую раскладку,
    сбрасывает счетчики и запускает игру.
    """
    state = get_state()
    board_w = state['board_w']
    board_h = state['board_h']

    max_tiles = board_w * board_h

    # 1. Сброс переменных для перемешивания
    flat_tiles_shuffled = []
    is_shuffling_solvable = False

    # 2. Перемешивание, пока поле не станет решаемым
    while not is_shuffling_solvable:

        # 2a. Создаем линеаризованный список плиток (от 1 до N-1)
        flat_tiles = list(range(1, max_tiles))
        random.shuffle(flat_tiles)

        # 2b. Добавляем пустую плитку (0) и перемещаем ее случайным образом
        flat_tiles_with_zero = flat_tiles + [0]

        # Перемещаем 0 в случайное место для игры
        idx_to_move_0 = random.randint(0, max_tiles - 1)

        # Удаляем 0 из конца и вставляем на случайную позицию
        flat_tiles_shuffled = flat_tiles_with_zero[:-1]
        flat_tiles_shuffled.insert(idx_to_move_0, 0)

        # 2c. Проверяем решаемость
        if is_solvable(board_w, board_h, flat_tiles_shuffled):
            is_shuffling_solvable = True
        else:
            print("ЛОГ ИГРЫ: Сгенерирована нерешаемая раскладка. Повторное перемешивание.")

    # 3. Восстанавливаем 2D массив из решаемого плоского списка
    new_board = []
    for i in range(board_h):
        new_board.append(flat_tiles_shuffled[i * board_w: (i + 1) * board_w])

    # 4. Обновление состояния: Сохраняем поле и рассчитываем S_initial
    set_state('tiles', new_board)

    # Расчет и сохранение початкової складності E
    S_initial_value = calculate_initial_S(new_board, board_w, board_h)
    set_state('S_initial', S_initial_value)

    # Сброс игровых счетчиков
    set_state('moves_count', 0)
    set_state('time_elapsed', 0.0)
    set_state('coeff_e', 0.0)  # Сброс E
    set_state('is_playing', True)

    print(
        f"ЛОГ ИГРЫ: Поле перемешано (гарантированно решаемо). S_initial: {S_initial_value}. Таймер и счетчик ходов запущены.")
    # 5. Восстанавливаем 2D массив из решаемого плоского списка
    new_board = []
    for i in range(board_h):
        new_board.append(flat_tiles_shuffled[i * board_w: (i + 1) * board_w])

    # 6. Обновление состояния
    set_state('tiles', new_board)
    set_state('moves_count', 0)
    set_state('time_elapsed', 0.0)
    set_state('is_playing', True)

    print("ЛОГ ИГРЫ: Поле перемешано (гарантированно решаемо). Таймер и счетчик ходов запущены.")

# game/logic.py (Вставьте этот блок в конец файла)

def get_empty_tile_pos(tiles, board_w, board_h):
    """Находит координаты пустой ячейки (0)."""
    for r in range(board_h):
        for c in range(board_w):
            if tiles[r][c] == 0:
                return r, c
    return -1, -1  # Не должно происходить


def calculate_k(state):
    """
    Рассчитывает коэффициент эффективности K по логарифмической шкале.
    K = (1000 * W * H) / (Time * Moves)
    """
    moves = state['moves_count']
    time = state['time_elapsed']
    board_w = state['board_w']
    board_h = state['board_h']

    # Жесткое условие: K начинает считаться, только если и ходы, и время > 0
    if moves == 0 or time < 1:
        return 0.0

    # Площадь поля (N) и множитель
    N = board_w * board_h
    K_MULTIPLIER = 1000
    MAX_K = N * K_MULTIPLIER  # Новый теоретический максимум

    # Расчет K по формуле
    k_value = (K_MULTIPLIER * N) / (time * moves)

    # Ограничиваем K новым максимумом
    k_value = min(k_value, MAX_K)

    return round(k_value, 4)


# game/logic.py (Обновленная функция make_move)

def make_move(tile_row, tile_col):
    """
    Обрабатывает ход, сдвигает ряд/столбец и проверяет условие победы.
    """
    state = get_state()
    if not state['is_playing']:
        return

    # --- 1. ИНИЦИАЛИЗАЦИЯ (ОТСУТСТВУЮЩИЙ КОД) ---
    tiles = state['tiles']
    board_w = state['board_w']
    board_h = state['board_h']

    empty_r, empty_c = get_empty_tile_pos(tiles, board_w, board_h)
    move_made = False  # Инициализация флага
    # ---------------------------------------------

    # --- 2. РЕАЛЬНАЯ ЛОГИКА СДВИГА (КОТОРУЮ ВЫ ПРОПУСТИЛИ) ---

    # Сдвиг по горизонтали (в одном ряду)
    if tile_row == empty_r:
        r = tile_row

        if tile_col < empty_c:
            # Сдвиг влево
            for c in range(empty_c, tile_col, -1):
                tiles[r][c] = tiles[r][c - 1]
            tiles[r][tile_col] = 0
            move_made = True
        elif tile_col > empty_c:
            # Сдвиг вправо
            for c in range(empty_c, tile_col):
                tiles[r][c] = tiles[r][c + 1]
            tiles[r][tile_col] = 0
            move_made = True

    # Сдвиг по вертикали (в одном столбце)
    elif tile_col == empty_c:
        c = tile_col

        if tile_row < empty_r:
            # Сдвиг вверх
            for r in range(empty_r, tile_row, -1):
                tiles[r][c] = tiles[r - 1][c]
            tiles[tile_row][c] = 0
            move_made = True
        elif tile_row > empty_r:
            # Сдвиг вниз
            for r in range(empty_r, tile_row):
                tiles[r][c] = tiles[r + 1][c]
            tiles[tile_row][c] = 0
            move_made = True

    # --------------------------------------------------------

    # 3. Обновление статистики (только если ход был сделан)
    if move_made:
        set_state('moves_count', state['moves_count'] + 1)

        # Расчет и обновление K
        k_value = calculate_k(state)
        set_state('coeff_k', k_value)

        set_state('tiles', tiles)

        # 4. ПРОВЕРКА ПОБЕДЫ
        if is_solved(state):
            set_state('is_playing', False)
            print(f"--- 🎉 ПОБЕДА! 🎉 ---")
            print(f"Финальный K: {k_value:.4f}")
        else:
            print(f"ЛОГ ИГРЫ: Ряд/столбец сдвинут. Ходов: {state['moves_count']}. K: {k_value}")
    else:
        print("ЛОГ ИГРЫ: Клик не привел к сдвигу (не на одной линии с 0).")