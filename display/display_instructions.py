# display/display_instructions.py

import tkinter as tk
from tkinter import ttk
from ui.elements import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from ui.handler_tkinter import set_next_scene, get_next_scene

# Хранит объект главного окна Tkinter
root_window = None


def close_scene_and_switch(next_scene_name):
    """Устанавливает следующую сцену и закрывает текущее окно Tkinter."""
    global root_window

    set_next_scene(next_scene_name)
    if root_window:
        root_window.destroy()


def show_instructions():
    """Создает и отображает окно инструкций."""
    global root_window

    root_window = tk.Tk()
    root_window.title(WINDOW_TITLE + " - Инструкции")

    # Центрирование окна
    screen_width = root_window.winfo_screenwidth()
    screen_height = root_window.winfo_screenheight()
    x = (screen_width / 2) - (WINDOW_WIDTH / 2)
    y = (screen_height / 2) - (WINDOW_HEIGHT / 2)
    root_window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{int(x)}+{int(y)}')
    root_window.resizable(False, False)

    main_frame = ttk.Frame(root_window, padding="20 20 20 20")
    main_frame.pack(fill='both', expand=True)

    # 1. Заголовок
    ttk.Label(
        main_frame,
        text="Правила игры 'Пятнашки' (15-puzzle)",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # 2. Текстовое поле с инструкциями
    instructions_text = """
Цель: Расположить все плитки по порядку, от 1 до 15.

Правила:
1. Игровое поле представляет собой квадрат 4x4, содержащий 15 пронумерованных плиток и одно пустое место.
2. Вы можете переместить плитку в пустое место, если она находится непосредственно рядом с ним (по горизонтали или вертикали).
3. Ход засчитывается, когда плитка перемещена.
4. Игра заканчивается, когда все плитки расположены по порядку, а пустое место находится в правом нижнем углу.

Удачи в решении головоломки!
    """

    ttk.Label(
        main_frame,
        text=instructions_text,
        justify=tk.LEFT,
        font=("Arial", 12)
    ).pack(pady=20, fill='x')

    # 3. Кнопки для перехода
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)

    # Кнопка "Назад"
    ttk.Button(
        button_frame,
        text="Назад (Приветствие)",
        command=lambda: close_scene_and_switch('greetings')
    ).pack(side=tk.LEFT, padx=10)

    # Кнопка "Далее" (Переход в меню)
    ttk.Button(
        button_frame,
        text="Начать игру (Меню)",
        command=lambda: close_scene_and_switch('menu')
    ).pack(side=tk.LEFT, padx=10)

    root_window.mainloop()

    return get_next_scene()