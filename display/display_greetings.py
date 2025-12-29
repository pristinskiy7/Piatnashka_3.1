# display/display_greetings.py

import tkinter as tk
from tkinter import ttk
# Импортируем общие константы
from ui.elements import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, COLOR_BACKGROUND
# Импортируем обработчик для переключения сцены
from ui.handler_tkinter import set_next_scene, get_next_scene

# Хранит объект главного окна Tkinter
root_window = None


def start_scene(next_scene_name):
    """Обработчик нажатия кнопки: устанавливает следующую сцену и закрывает окно."""
    global root_window

    set_next_scene(next_scene_name)
    if root_window:
        root_window.destroy()  # Закрываем окно Tkinter, чтобы main.py мог продолжить


def show_greetings():
    """Создает и отображает окно приветствия."""
    global root_window

    root_window = tk.Tk()
    root_window.title(WINDOW_TITLE)

    # Центрирование окна
    screen_width = root_window.winfo_screenwidth()
    screen_height = root_window.winfo_screenheight()
    x = (screen_width / 2) - (WINDOW_WIDTH / 2)
    y = (screen_height / 2) - (WINDOW_HEIGHT / 2)
    root_window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{int(x)}+{int(y)}')
    root_window.resizable(False, False)

    # 1. Приветственный текст
    ttk.Label(
        root_window,
        text="Добро пожаловать в игру 'Суперпятнашки'!",
        font=("Arial", 24, "bold")
    ).pack(pady=50)

    ttk.Label(
        root_window,
        text="Версия 3.1. Для начала нажмите 'Продолжить'",
        font=("Arial", 14)
    ).pack(pady=10)

    # 2. Кнопка для перехода к инструкциям
    ttk.Button(
        root_window,
        text="Продолжить",
        command=lambda: start_scene('instructions')
        # При нажатии вызывается start_scene('instructions')
    ).pack(pady=20)

    # Запускаем цикл обработки событий Tkinter.
    # Код блокируется здесь до вызова root_window.destroy()
    root_window.mainloop()

    # После закрытия окна, возвращаем имя следующей сцены,
    # которое было установлено в start_scene()
    return get_next_scene()