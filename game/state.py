# game/state.py
# game/state.py

# Инициализируем пустое состояние игры.
# Используем _GAME_STATE, чтобы избежать конфликтов при импорте.
_GAME_STATE = {
    'player_name': None,
    'board_w': 0,
    'board_h': 0,
    'tiles': [],  # Массив 2D, содержащий числа 1..N-1 и 0 (пустая клетка)
    'moves_count': 0,  # Количество сделанных ходов
    'time_elapsed': 0.0,  # Прошедшее время
    'game_active': False,
    'coeff_k': 0.0,  # Коэффициент K
    'is_playing': False  # Флаг для таймера (начат ли отсчет)
}


def init_game_state(player_name, board_w, board_h):
    """
    Заполняет глобальное состояние игры начальными параметрами и создает упорядоченное поле.
    """
    global _GAME_STATE

    # 1. Создание упорядоченного массива плиток (N x M)
    board_tiles = []
    tile_count = 1

    for r in range(board_h):
        row = []
        for c in range(board_w):
            if tile_count < board_w * board_h:
                row.append(tile_count)
                tile_count += 1
            else:
                # Последняя ячейка - пустая (0)
                row.append(0)
        board_tiles.append(row)

    # 2. Обновление глобального состояния
    _GAME_STATE['player_name'] = player_name
    _GAME_STATE['board_w'] = board_w
    _GAME_STATE['board_h'] = board_h
    _GAME_STATE['tiles'] = board_tiles  # <-- Записываем созданное поле

    # 3. Сброс статистики
    _GAME_STATE['moves_count'] = 0
    _GAME_STATE['time_elapsed'] = 0.0
    _GAME_STATE['coeff_k'] = 0.0
    _GAME_STATE['game_active'] = True
    _GAME_STATE['is_playing'] = False  # Начнем отсчет по клику на поле

    print(f"ЛОГ: Состояние игры инициализировано для {player_name} ({board_w}x{board_h}).")


def get_state():
    """Возвращает текущее состояние игры.
    Используется в game_loop для отрисовки."""
    return _GAME_STATE


def set_state(key, value):
    """Обновляет значение в состоянии игры."""
    global _GAME_STATE
    _GAME_STATE[key] = value

# Нам нужно также изменить get_state в game_loop.py,
# чтобы он возвращал правильные ключи для отрисовки.