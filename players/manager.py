# players/manager.py
import json
import os

PLAYERS_FILE = "players.json"


def _read_players():
    if not os.path.exists(PLAYERS_FILE):
        return []
    try:
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print("Ошибка чтения JSON:", e)
        return []


def _write_players(players):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=4)


def load_players():
    """Гарантируем структуру: у каждого есть поля name, active, best_game, total."""
    players = _read_players()

    changed = False
    for p in players:
        if "active" not in p:
            p["active"] = False
            changed = True
        if "best_game" not in p:
            p["best_game"] = {
                "area": None,
                "time": None,
                "moves": None,
                "rating": None,
                "date": None
            }
            changed = True
        if "total" not in p:
            p["total"] = {
                "games": 0,
                "area": 0,
                "time": 0,
                "moves": 0,
                "rating": 0,
                "best_date": None
            }
            changed = True

    # если нет активного – сделаем первым активным
    if players and not any(p.get("active") for p in players):
        players[0]["active"] = True
        changed = True

    if changed:
        _write_players(players)

    return players


def save_players(players):
    """Сохраняем игроков как есть (используй осторожно)."""
    _write_players(players)


def add_player(name):
    name = name.strip()
    if not name:
        return

    players = load_players()

    # если уже есть такой – просто сделать его активным
    for p in players:
        if p["name"] == name:
            set_active_player(name)
            return

    players.append({
        "name": name,
        "active": False,
        "best_game": {
            "area": None,
            "time": None,
            "moves": None,
            "rating": None,
            "date": None
        },
        "total": {
            "games": 0,
            "area": 0,
            "time": 0,
            "moves": 0,
            "rating": 0,
            "best_date": None
        }
    })

    # если это первый игрок – сделать активным
    if len(players) == 1:
        players[0]["active"] = True

    _write_players(players)


def get_active_player():
    players = load_players()
    for p in players:
        if p.get("active"):
            return p["name"]
    return None


def set_active_player(name):
    players = load_players()
    found = False
    for p in players:
        if p["name"] == name:
            p["active"] = True
            found = True
        else:
            p["active"] = False

    if not found:
        return

    _write_players(players)


def save_result(player_name, w, h, moves, time_sec, date_str):
    """Сохраняем результат партии игрока: лучшая партия и суммарная статистика."""
    players = load_players()
    area = w * h
    rating = area / (time_sec * moves) if time_sec > 0 and moves > 0 else 0

    for p in players:
        if p["name"] == player_name:
            # обновляем суммарную статистику
            p["total"]["games"] += 1
            p["total"]["area"] += area
            p["total"]["time"] += time_sec
            p["total"]["moves"] += moves
            if p["total"]["time"] > 0 and p["total"]["moves"] > 0:
                p["total"]["rating"] = p["total"]["area"] / (p["total"]["time"] * p["total"]["moves"])

            # проверка лучшей партии
            current_best_rating = p["best_game"]["rating"] or 0
            if rating > current_best_rating:
                p["best_game"] = {
                    "area": area,
                    "time": time_sec,
                    "moves": moves,
                    "rating": rating,
                    "date": date_str
                }
                p["total"]["best_date"] = date_str

            break

    _write_players(players)


def delete_active_player():
    """Удаляет текущего активного игрока из списка и JSON."""
    players = load_players()
    active_index = None
    for i, p in enumerate(players):
        if p.get("active"):
            active_index = i
            break

    if active_index is None:
        print(">>> Нет активного игрока для удаления.")
        return False

    removed_name = players[active_index]["name"]
    del players[active_index]

    # если остались игроки — сделаем первого активным
    if players:
        players[0]["active"] = True

    _write_players(players)
    print(f">>> Игрок '{removed_name}' удалён из JSON.")
    return True