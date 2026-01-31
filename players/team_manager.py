# players/team_manager.py

import json
import os
import datetime

TEAM_FILE = 'team.json'
TEAM_KEY = 'team_name'

def reset_team():
    """Удаляет файл team.json, фактически распуская команду."""
    if os.path.exists(TEAM_FILE):
        try:
            os.remove(TEAM_FILE)
            print(f"ЛОГ: Файл команды {TEAM_FILE} удален.")
            return True
        except Exception as e:
            print(f"ЛОГ ОШИБКИ: Не удалось удалить файл {TEAM_FILE}: {e}")
            return False
    return False

def ensure_team_id():
    """Проверяет наличие team_id и создаёт его, если его нет (для старых команд)."""
    data = _load_team_full_data()
    if data and "team_id" not in data:
        name = data.get("team_name", "Unknown")
        created_at = datetime.datetime.now().isoformat(timespec='seconds')
        data["created_at"] = created_at
        data["team_id"] = f"{name}_{created_at.replace(':', '-')}"

        with open(TEAM_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"ЛОГ: Команде присвоен уникальный ID: {data['team_id']}")

def save_team_name(name):
    """Сохраняет название команды и время её создания (ID команды)."""
    # Если файл уже есть, не перезаписываем время создания, чтобы ID не менялся
    existing_team = _load_team_full_data()
    created_at = existing_team.get('created_at') if existing_team else datetime.datetime.now().isoformat(timespec='seconds')

    data = {
        "team_name": name,
        "created_at": created_at,
        "team_id": f"{name}_{created_at.replace(':', '-')}" # Уникальный ключ для Монго
    }
    try:
        with open(TEAM_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"ОШИБКА: {e}")
        return False

def _load_team_full_data():
    """Вспомогательная: грузит весь объект команды."""
    if not os.path.exists(TEAM_FILE): return {}
    try:
        with open(TEAM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def get_team_name():
    return _load_team_full_data().get("team_name")

def get_team_id():
    return _load_team_full_data().get("team_id")