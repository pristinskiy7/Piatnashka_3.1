# players/manager.py
# players/manager.py (Финальная версия, изолированная от других команд)
import json
import os
import datetime
from players.team_manager import get_team_name  # Для проверки наличия активной команды

PLAYERS_FILE = 'players.json'


# --- Вспомогательные функции для работы с файлом ---

def _load_players_data():
    """Загружает данные игроков и активного игрока из players.json."""
    if not os.path.exists(PLAYERS_FILE):
        # Структура по умолчанию: нет активного игрока, нет игроков
        return {"active_player": None, "players": {}}
    try:
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Убеждаемся, что это словарь и содержит нужные ключи
            if isinstance(data, dict) and 'players' in data:
                return data
            else:
                return {"active_player": None, "players": {}}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"active_player": None, "players": {}}


def _save_players_data(data):
    """Сохраняет данные игроков в players.json."""
    # Сохраняем только если команда существует (чтобы не сохранять пустые данные, если команда не создана)
    if not get_team_name():
        return False

    try:
        with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)
        return True
    except IOError as e:
        print(f"ОШИБКА: Не удалось сохранить данные игроков: {e}")
        return False


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
    """
    Возвращает список всех имен игроков в текущей активной команде.
    Возвращает пустой список, если команда не создана или игроков нет.
    """
    if not get_team_name():
        return []

    data = _load_players_data()

    # --- ИСПРАВЛЕНИЕ: ДОБАВЛЯЕМ ПРОВЕРКУ ТИПА В ГЕНЕРАТОРЕ ---
    # Мы извлекаем 'name' ТОЛЬКО если player является словарем (dict)
    names = [player.get('name')
             for player in data.get('players', [])
             if isinstance(player, dict)]

    return names


# players/manager.py

# ... (другие функции) ...

def save_current_player(name):
    """
    Устанавливает игрока активным. Если игрока нет, создает его,
    добавляя в список, и делает активным.
    """
    team_name = get_team_name()
    if not team_name:
        print("ЛОГ ОШИБКИ: Невозможно сохранить игрока без активной команды.")
        return False

    data = _load_players_data()
    name = name.strip()
    player_found = False

    # 1. Ищем игрока в списке.
    #    При этом сбрасываем флаг 'active' у всех других.
    for player in data['players']:
        if player['name'] == name:
            player_found = True
            player['active'] = True  # Устанавливаем текущего игрока
        else:
            player['active'] = False  # Сбрасываем флаг для других

    # 2. Если игрок не найден (т.е. это новый игрок)
    if not player_found:
        # 2a. Создаем объект нового игрока
        new_player_data = {
            "name": name,
            "active": True,
            "created_at": datetime.datetime.now().isoformat(timespec='seconds'),
            "best_game": {},
            "total": {'games': 0, 'moves': 0, 'time': 0}
        }
        # 2b. ДОБАВЛЕНИЕ: Используем .append() для списка (ИСПРАВЛЕНИЕ ОШИБКИ)
        data['players'].append(new_player_data)
        print(f"ЛОГ: Новый игрок '{name}' добавлен в команду '{team_name}'.")

    # 3. Устанавливаем игрока активным в корневом объекте
    data['active_player'] = name

    _save_players_data(data)
    print(f"ЛОГ: Игрок '{name}' выбран как активный в команде '{team_name}'.")
    return True


# Заглушка (как требовалось в game/state.py)
def save_result(*args, **kwargs):
    print("ЛОГ: Сохранение результата (заглушка)...")
    pass