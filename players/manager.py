# players/manager.py

# players/manager.py (Финальная версия, изолированная от других команд)
import json
import os
import datetime
# Убедитесь, что вы импортируете обе нужные функции, если reset_team вызывается в delete_player
from players.team_manager import get_team_name, reset_team


PLAYERS_FILE = 'players.json'

# ------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ КОМАНДЫ (Временно) -------------------
# Эти функции нужны для проверки и сброса команды.



# ----------------------------------------------------------------------------------
# --- Вспомогательные функции для работы с файлом ---

def _load_players_data():
    """Загружает данные игроков и активного игрока, гарантируя структуру по умолчанию."""
    default_data = {"active_player": None, "players": []}

    if not os.path.exists(PLAYERS_FILE):
        return default_data

    try:
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            if not isinstance(data, dict):
                return default_data

            # Гарантия 1: active_player
            if 'active_player' not in data:
                data['active_player'] = default_data['active_player']

            # Гарантия 2: players должен быть списком
            if 'players' not in data or not isinstance(data['players'], list):
                data['players'] = default_data['players']

            return data

    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"ЛОГ ПРЕДУПРЕЖДЕНИЕ: Ошибка при загрузке {PLAYERS_FILE} ({e}). Возврат к значениям по умолчанию.")
        return default_data


def _save_players_data(data):
    """Сохраняет данные игроков в players.json."""
    try:
        with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ЛОГ ОШИБКИ: Не удалось сохранить данные игроков: {e}")
        return False


def delete_player(name_to_delete):
    """
    Удаляет игрока из списка.
    Если удаляется последний игрок, удаляет команду.
    """
    team_name = get_team_name()
    if not team_name:
        print("ЛОГ ОШИБКИ: Невозможно удалить игрока без активной команды.")
        return False

    data = _load_players_data()
    name_to_delete = name_to_delete.strip()

    initial_count = len(data['players'])

    # 1. Удаление игрока
    data['players'] = [
        player
        for player in data['players']
        if isinstance(player, dict) and player.get('name') != name_to_delete
    ]

    if len(data['players']) == initial_count:
        print(f"ЛОГ ОШИБКИ: Игрок '{name_to_delete}' не найден для удаления.")
        return False

        # 2. Обработка active_player до проверки списка
    deleted_was_active = (data.get('active_player') == name_to_delete)

    # 3. Проверка: Если игроков не осталось (ФИНАЛЬНЫЙ ШТРИХ)
    if not data['players']:

        # 3а. Сбрасываем active_player и сохраняем пустой список игроков
        data['active_player'] = None
        _save_players_data(data)



    else:
        # 4. Если игроки остались
        if deleted_was_active:
            # Делаем первого игрока в новом списке активным
            data['active_player'] = data['players'][0]['name']

        _save_players_data(data)  # Сохраняем обновленный список и active_player

    return True


# --- Основные функции логики ---

# players/manager.py

def get_current_player_name():
    """
    Возвращает имя активного игрока.
    Возвращает None, если активный игрок не назначен или команда не создана.
    """
    if not get_team_name():
        return None

    data = _load_players_data()
    active_player_name = data.get('active_player')

    # 1. Возвращаем явно активного игрока, если его имя есть в корневой записи
    if active_player_name:

        # ДОБАВЛЕНА ЗАЩИТА: Проверяем, что игрок с таким именем есть в списке players
        players_list = data.get('players', [])
        player_exists = any(
            player.get('name') == active_player_name and isinstance(player, dict) for player in players_list)

        if player_exists:
            return active_player_name

        # Если active_player_name указан, но игрок не найден в списке,
        # сбрасываем active_player на None, чтобы избежать ошибок
        data['active_player'] = None
        _save_players_data(data)

    # 2. Если активного игрока нет, но игроки есть в списке, делаем первого активным по умолчанию
    players_list = data.get('players', [])
    if players_list and players_list[0].get('name'):
        first_player_name = players_list[0]['name']

        # Делаем первого игрока активным
        data['active_player'] = first_player_name
        _save_players_data(data)
        return first_player_name

    # Если команда есть, но игроков нет (players_list пуст)
    return None


def get_all_player_names():
    """Возвращает список имен всех игроков в команде."""
    data = _load_players_data()
    return [player.get('name') for player in data['players'] if isinstance(player, dict) and 'name' in player]


# players/manager.py

# ... (другие функции) ...

def save_current_player(player_name):
    """
    Сохраняет игрока (если новый) и делает его активным.
    """
    player_name = player_name.strip()

    # 1. ЗАЩИТА: Блокируем сохранение служебных имен и пустых строк
    if not player_name or player_name.lower() == "добавить нового игрока":
        print("ЛОГ ОШИБКИ: Попытка сохранить недопустимое имя игрока.")
        return False

    data = _load_players_data()

    # 2. Проверка, существует ли игрок
    is_new_player = True
    for player in data['players']:
        if player.get('name') == player_name:
            is_new_player = False
            break

    # 3. Если игрок новый, добавляем его с данными по умолчанию
    if is_new_player:
        new_player_data = {
            "name": player_name,

            # ИСПРАВЛЕНИЕ: Вызов должен быть datetime.datetime.now()
            "created_at": datetime.datetime.now().isoformat(timespec='seconds'),
            "best_game": {},  # {'moves': 50, 'time': 120, 'date': '...'}
            "total": {"games": 0, "moves": 0, "time": 0}
        }
        data['players'].append(new_player_data)

    # 4. Делаем игрока активным
    data['active_player'] = player_name

    # 5. Сохраняем и возвращаем результат
    return _save_players_data(data)


def delete_player(name_to_delete):
    """
    Удаляет игрока из списка.
    Если удаляется последний игрок, удаляет команду.
    """
    team_name = get_team_name()
    if not team_name:
        print("ЛОГ ОШИБКИ: Невозможно удалить игрока без активной команды.")
        return False

    data = _load_players_data()
    name_to_delete = name_to_delete.strip()

    initial_count = len(data['players'])

    # 1. Удаление игрока
    data['players'] = [
        player
        for player in data['players']
        if isinstance(player, dict) and player.get('name') != name_to_delete
    ]

    if len(data['players']) == initial_count:
        print(f"ЛОГ ОШИБКИ: Игрок '{name_to_delete}' не найден для удаления.")
        return False

        # 2. Обработка active_player до проверки списка
    deleted_was_active = (data.get('active_player') == name_to_delete)

    # 3. Проверка: Если игроков не осталось (ФИНАЛЬНЫЙ ШТРИХ)
    if not data['players']:

        # 3а. Сбрасываем active_player и сохраняем пустой список игроков
        data['active_player'] = None
        _save_players_data(data)

        # 3б. Удаляем команду (!!! ВОССТАНОВЛЕННЫЙ КОД !!!)
        reset_team()
        print(f"ЛОГ: Последний игрок удален. Команда '{team_name}' распущена.")

    else:
        # 4. Если игроки остались
        if deleted_was_active:
            # Делаем первого игрока в новом списке активным
            data['active_player'] = data['players'][0]['name']

        _save_players_data(data)  # Сохраняем обновленный список и active_player

    return True

# Заглушка (как требовалось в game/state.py)
def save_result(*args, **kwargs):
    print("ЛОГ: Сохранение результата (заглушка)...")
    pass