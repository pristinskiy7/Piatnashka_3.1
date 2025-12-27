# settings/manager.py

import json
import os

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "width_mode": "random",
    "height_mode": "random",
    "width_value": 6,
    "height_value": 6,
    "team_name": ""   # ← новое поле
}

TEAM_NAME = ""

def save_team(name: str):
    global TEAM_NAME
    TEAM_NAME = name

    # Загружаем текущие настройки
    settings = load_settings()
    settings["team_name"] = TEAM_NAME

    # Сохраняем обратно в файл
    save_settings(settings)

    print(f"[settings.manager] Сохранено название команды: {TEAM_NAME}")


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # нормализуем ключи
        for k, v in DEFAULT_SETTINGS.items():
            if k not in data:
                data[k] = v
        return data
    except Exception as e:
        print("Ошибка чтения settings.json:", e)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def update_settings(w_mode, h_mode, w_val, h_val):
    settings = {
        "width_mode": w_mode,
        "height_mode": h_mode,
        "width_value": w_val,
        "height_value": h_val
    }
    save_settings(settings)