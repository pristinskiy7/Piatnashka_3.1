# history/manager.py

import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Ошибка чтения history.json:", e)
        return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def add_game(player, width, height, moves, time_sec):
    history = load_history()
    area = width * height
    coef = area / (moves * time_sec) if moves > 0 and time_sec > 0 else 0
    date_str = datetime.now().isoformat(timespec="seconds")

    if player not in history:
        # первая игра
        history[player] = {
            "best_game": {
                "area": area,
                "moves": moves,
                "time": time_sec,
                "coef": coef,
                "date": date_str
            },
            "summary": {
                "area_sum": area,
                "moves_sum": moves,
                "time_sum": time_sec,
                "coef": coef
            }
        }
    else:
        # обновляем summary
        summary = history[player]["summary"]
        summary["area_sum"] += area
        summary["moves_sum"] += moves
        summary["time_sum"] += time_sec
        summary["coef"] = summary["area_sum"] / (summary["moves_sum"] * summary["time_sum"]) \
            if summary["moves_sum"] > 0 and summary["time_sum"] > 0 else 0

        # проверяем лучшую игру
        best = history[player]["best_game"]
        if coef > best["coef"]:
            history[player]["best_game"] = {
                "area": area,
                "moves": moves,
                "time": time_sec,
                "coef": coef,
                "date": date_str
            }

    save_history(history)