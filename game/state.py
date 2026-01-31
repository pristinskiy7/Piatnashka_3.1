# game/state.py

# Глобальная переменная для хранения состояния
_GAME_STATE = {
    'player_name': None,
    'board_w': 0,
    'board_h': 0,
    'tiles': [],  # Массив 2D (числа 1..N-1 и 0)
    'moves_count': 0,  # Количество сделанных ходов
    'time_elapsed': 0.0,  # Прошедшее время

    # --- НОВАЯ ЭКОНОМИКА (XP SYSTEM) ---
    'md_initial': 0,  # Начальная дистанция Манхэттена (базовая сложность)
    'coeff_k': 0.0,  # Текущий прогноз XP за эту игру
    'total_xp': 0,  # Общий накопленный опыт игрока (из файла профиля)
    'rank_title': "Новичок",  # Текущее звание игрока
    # -----------------------------------

    'game_active': False,
    'is_playing': False  # True, если таймер запущен
}


def init_game_state(player_name, board_w, board_h, total_xp=0, rank_title="Новичок"):
    """
    Инициализирует состояние игры.
    Теперь принимает данные о прогрессе игрока для отображения ранга.
    """
    global _GAME_STATE

    # 1. Создание упорядоченного массива плиток
    board_tiles = []
    tile_count = 1
    for r in range(board_h):
        row = []
        for c in range(board_w):
            if tile_count < board_w * board_h:
                row.append(tile_count)
                tile_count += 1
            else:
                row.append(0)
        board_tiles.append(row)

    # 2. Обновление состояния
    _GAME_STATE['player_name'] = player_name
    _GAME_STATE['board_w'] = board_w
    _GAME_STATE['board_h'] = board_h
    _GAME_STATE['tiles'] = board_tiles

    # Сброс текущей статистики
    _GAME_STATE['moves_count'] = 0
    _GAME_STATE['time_elapsed'] = 0.0
    _GAME_STATE['md_initial'] = 0
    _GAME_STATE['coeff_k'] = 0.0

    # Данные прогресса
    _GAME_STATE['total_xp'] = total_xp
    _GAME_STATE['rank_title'] = rank_title

    _GAME_STATE['game_active'] = True
    _GAME_STATE['is_playing'] = False

    print(f"ЛОГ: Состояние инициализировано. Игрок: {player_name}, Ранг: {rank_title}")


def get_state():
    """Возвращает текущее состояние игры."""
    return _GAME_STATE


def set_state(key, value):
    """Обновляет значение в состоянии игры."""
    global _GAME_STATE
    if key in _GAME_STATE:
        _GAME_STATE[key] = value