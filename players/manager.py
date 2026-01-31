# players/manager.py

import json
import os
from players.team_manager import reset_team  # Импортируем функцию удаления команды

PLAYERS_FILE = 'players.json'


def _load_players_data():
    if not os.path.exists(PLAYERS_FILE):
        return {"players": [], "current_player": None}
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_players_data(data):
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_new_player(name):
    data = _load_players_data()
    if any(p['name'] == name for p in data['players']):
        return False
    new_p = {
        "name": name,
        "total": {"xp": 0, "moves": 0, "time": 0},
        "best_game": None
    }
    data['players'].append(new_p)
    data['current_player'] = name
    _save_players_data(data)
    return True


def delete_player(name):
    data = _load_players_data()
    data['players'] = [p for p in data['players'] if p['name'] != name]

    if data['current_player'] == name:
        data['current_player'] = data['players'][0]['name'] if data['players'] else None

    _save_players_data(data)

    # ЕСЛИ ИГРОКОВ НЕ ОСТАЛОСЬ — РАСПУСКАЕМ КОМАНДУ
    if not data['players']:
        reset_team()
        if os.path.exists(PLAYERS_FILE):
            os.remove(PLAYERS_FILE)
    return True


# Остальные функции (get_current_player_name и т.д.) оставь как были
def get_current_player_name():
    return _load_players_data().get('current_player')


def save_current_player(name):
    data = _load_players_data()
    data['current_player'] = name
    _save_players_data(data)


def get_all_player_names():
    return [p['name'] for p in _load_players_data()['players']]


# players/manager.py (ДОБАВИТЬ В КОНЕЦ)

def save_result(moves, time_spent, xp_gained, board_size):
    """Сохраняет результат игры в профиль игрока и обновляет статистику."""
    data = _load_players_data()
    current_name = data.get('current_player')

    if not current_name:
        return

    for p in data['players']:
        if p['name'] == current_name:
            # Обновляем общий счет
            p['total']['xp'] += xp_gained
            p['total']['moves'] += moves
            p['total']['time'] += time_spent

            # Проверяем, лучший ли это результат (по XP)
            new_record = {
                "moves": moves,
                "time": time_spent,
                "xp": xp_gained,
                "size": f"{board_size[0]}x{board_size[1]}"
            }

            if p.get('best_game') is None or xp_gained > p['best_game'].get('xp', 0):
                p['best_game'] = new_record
                print(f"ЛОГ: Новый рекорд для {current_name}!")

            break

    _save_players_data(data)
    print(f"ЛОГ: Результат сохранен для {current_name}. +{xp_gained} XP")