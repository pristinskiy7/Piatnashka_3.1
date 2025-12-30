# settings/preferences.py
# settings/preferences.py

import json
import os

PREFERENCES_FILE = 'settings.json'
# Определяем константы для минимального и максимального размера
MIN_SIZE = 4
MAX_SIZE = 10
DEFAULT_SIZE = 4  # <--- Добавьте эту константу, если её нет


def _load_preferences():
    """Загружает настройки из файла или возвращает настройки по умолчанию."""
    default = {
        "board_w": DEFAULT_SIZE,
        "board_h": DEFAULT_SIZE,
    }

    if not os.path.exists(PREFERENCES_FILE):
        return default

    try:
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Проверка целостности загруженных данных
            w = data.get('board_w')
            h = data.get('board_h')

            # Валидация W
            if not (isinstance(w, int) and MIN_SIZE <= w <= MAX_SIZE or w == "RANDOM"):
                data['board_w'] = default['board_w']

            # Валидация H
            if not (isinstance(h, int) and MIN_SIZE <= h <= MAX_SIZE or h == "RANDOM"):
                data['board_h'] = default['board_h']

            return data

    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save_preferences(data):
    """Сохраняет настройки в файл settings.json."""
    try:
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


# --- ФУНКЦИИ, КОТОРЫЕ ТРЕБУЕТСЯ ИМПОРТИРОВАТЬ В display_menu.py ---

def get_board_preferences():  # <--- ЭТА ФУНКЦИЯ ДОЛЖНА СУЩЕСТВОВАТЬ
    """Возвращает текущие настройки размера поля (W, H).
    W и H могут быть int (4-10) или строкой 'RANDOM'."""
    data = _load_preferences()
    return {
        'w': data.get('board_w', DEFAULT_SIZE),
        'h': data.get('board_h', DEFAULT_SIZE)
    }


def set_board_preferences(w_value, h_value):  # <--- ЭТА ФУНКЦИЯ ДОЛЖНА СУЩЕСТВОВАТЬ
    """Сохраняет новые настройки размера поля (W и H)."""

    # 1. Валидация перед сохранением
    valid_w = isinstance(w_value, int) and MIN_SIZE <= w_value <= MAX_SIZE or w_value == "RANDOM"
    valid_h = isinstance(h_value, int) and MIN_SIZE <= h_value <= MAX_SIZE or h_value == "RANDOM"

    if not valid_w or not valid_h:
        return False

        # 2. Создаем новый словарь, содержащий ТОЛЬКО нужные ключи
    data_to_save = {
        'board_w': w_value,
        'board_h': h_value
    }

    return _save_preferences(data_to_save)