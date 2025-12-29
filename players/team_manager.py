# players/team_manager.py

import json
import os

# Имя файла для хранения названия команды
TEAM_FILE = 'team.json'
TEAM_KEY = 'team_name'


def get_team_name():
    """Загружает название команды из team.json. Возвращает None, если файла нет, он поврежден или имеет неверный формат."""
    if not os.path.exists(TEAM_FILE):
        return None
    try:
        with open(TEAM_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # --- ИСПРАВЛЕНИЕ: ПРОВЕРКА ТИПА ---
            if isinstance(data, dict):
                # Если это словарь, используем метод get()
                return data.get(TEAM_KEY)
            else:
                # Если это не словарь (например, список), возвращаем None
                print(
                    f"ОШИБКА: Файл {TEAM_FILE} содержит некорректный формат данных (ожидается dict, получен {type(data).__name__}).")
                return None

    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл поврежден или пуст, считаем, что команды нет
        return None


def save_team_name(name):
    """Сохраняет название команды в team.json."""
    data = {
        TEAM_KEY: name
    }
    try:
        with open(TEAM_FILE, 'w', encoding='utf-8') as f:
            # Используем indent=4 для красивого форматирования JSON
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"ЛОГ: Название команды '{name}' сохранено в {TEAM_FILE}.")
        return True
    except IOError as e:
        print(f"ОШИБКА: Не удалось сохранить название команды: {e}")
        return False

# players/team_manager.py

# ... (после save_team_name) ...

def reset_team():
    """Удаляет файл team.json, распуская команду."""
    if os.path.exists(TEAM_FILE):
        try:
            os.remove(TEAM_FILE)
            print(f"ЛОГ: Файл команды {TEAM_FILE} удален.")
            return True
        except Exception as e:
            # Сюда попадают ошибки доступа или прав
            print(f"ЛОГ ОШИБКИ: Не удалось удалить файл {TEAM_FILE}: {e}")
            return False
    return False