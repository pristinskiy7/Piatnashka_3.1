# main.py (Обновленный)

import sys
# Импортируем модули сцен
from display.display_greetings import show_greetings
from display.display_instructions import show_instructions
from display.display_menu import show_menu  # <--- НОВЫЙ ИМПОРТ

# Глобальная переменная для управления текущей сценой
current_scene = 'greetings'


def main():
    """Главный цикл и менеджер сцен."""
    global current_scene

    while current_scene != 'exit':

        if current_scene == 'greetings':
            print("--- Запуск Сцены: Приветствие ---")
            current_scene = show_greetings()

        elif current_scene == 'instructions':
            print("--- Запуск Сцены: Инструкции ---")
            current_scene = show_instructions()

        elif current_scene == 'menu':
            print("--- Запуск Сцены: Меню ---")
            current_scene = show_menu()  # <--- ИСПОЛЬЗУЕМ НОВУЮ ФУНКЦИЮ

        elif current_scene == 'game':
            print("--- Запуск Сцены: Игра ---")
            # current_scene = run_game() # пока не реализовано
            current_scene = 'results'  # Временно переходим к результатам

        elif current_scene == 'results':
            print("--- Запуск Сцены: Результаты ---")
            # current_scene = show_results() # пока не реализовано
            current_scene = 'exit'

        elif current_scene == 'exit':
            print("--- Завершение программы ---")
            break

        else:
            print(f"Ошибка: Неизвестная сцена: {current_scene}. Выход.")
            break


if __name__ == "__main__":
    main()