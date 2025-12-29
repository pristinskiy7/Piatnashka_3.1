# display/display_menu.py
import tkinter as tk
from tkinter import ttk
from ui.elements import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from ui.handler_tkinter import set_next_scene, get_next_scene

# Новые импорты для работы с идентификацией
from players.manager import get_current_player_name, save_current_player, get_all_player_names # <--- ДОБАВЛЕН НОВЫЙ ИМПОРТ
from players.team_manager import get_team_name, save_team_name  # <--- НОВЫЙ ИМПОРТ

root_window = None
player_name_var = None
team_name_var = None  # Переменная для хранения имени новой команды
current_team_name = None  # Фактическое имя существующей команды


def handle_create_team():
    """Обработчик кнопки: сохраняет новое имя команды и перезагружает меню."""
    global root_window

    new_name = team_name_var.get().strip()
    if new_name and len(new_name) > 2:
        # 1. Сохраняем имя команды
        save_team_name(new_name)

        # 2. Перезапускаем сцену меню, чтобы показать поле выбора игрока
        set_next_scene('menu')  # Говорим main.py, что нужно перезапустить 'menu'
        if root_window:
            root_window.destroy()
    else:
        # Простая валидация
        tk.messagebox.showerror("Ошибка", "Имя команды должно содержать минимум 3 символа.")


def close_scene_and_switch(next_scene_name):
    """Устанавливает следующую сцену и закрывает текущее окно Tkinter."""
    global root_window, current_team_name

    # Разрешаем переход к игре, только если команда УЖЕ создана
    if current_team_name is None and next_scene_name == 'game':
        tk.messagebox.showerror("Ошибка", "Сначала необходимо создать команду.")
        return

        # 1. Если мы переходим к ИГРЕ, сохраняем выбранного игрока
    if next_scene_name == 'game':
        player_name = player_name_var.get().strip()
        if not player_name:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, введите имя игрока.")
            return  # Отменяем переход, если имя игрока пустое

        save_current_player(player_name)

    set_next_scene(next_scene_name)
    if root_window:
        root_window.destroy()


def setup_team_creation_section(parent_frame):
    """Отображает секцию для ввода и создания новой команды."""
    global team_name_var

    team_name_var = tk.StringVar()

    ttk.Label(
        parent_frame,
        text="Создание Команды:",
        font=("Arial", 16, "bold")
    ).pack(pady=(20, 10))

    input_frame = ttk.Frame(parent_frame)
    input_frame.pack(pady=10)

    # 1. Текстбокс для имени команды
    ttk.Entry(
        input_frame,
        textvariable=team_name_var,
        width=30,
        font=("Arial", 14)
    ).pack(side=tk.LEFT, padx=10)

    # 2. Кнопка создания
    ttk.Button(
        input_frame,
        text="Создать Команду",
        command=handle_create_team
    ).pack(side=tk.LEFT, padx=10)

    ttk.Label(
        parent_frame,
        text="Сначала назовите команду, чтобы начать игру.",
        font=("Arial", 10)
    ).pack()


def handle_player_selection(event=None):
    """Обработчик для кнопки 'Начать Игру' (если выбрано имя) или 'Добавить Игрока'."""
    global root_window

    player_name = player_name_var.get().strip()

    # 1. Если выбрана строка-приглашение, считаем это ошибкой (пользователь не выбрал имя)
    if not player_name or player_name == "Добавить нового игрока":
        tk.messagebox.showerror("Ошибка", "Пожалуйста, выберите или введите корректное имя игрока.")
        return

        # 2. Если имя выбрано/введено, сохраняем/добавляем игрока и делаем его активным
    success = save_current_player(player_name)

    if success:
        # 3. Перезапускаем сцену меню, чтобы обновить отображение
        set_next_scene('menu')
        if root_window:
            root_window.destroy()
    else:
        tk.messagebox.showerror("Ошибка", "Не удалось сохранить игрока.")


def handle_combobox_selection(event):
    """
    Обработчик, который срабатывает при выборе имени из Combobox.
    Если выбрано имя игрока - делаем его активным.
    Если выбрано "Добавить нового игрока" - очищаем поле и ждем ввода.
    """
    global root_window

    selected_name = player_name_var.get().strip()

    if selected_name == "Добавить нового игрока":
        # Если выбрана специальная строка, очищаем поле для ввода
        player_name_var.set("")
        # Меняем фокус, чтобы пользователь мог сразу печатать
        event.widget.focus_set()
        # Выход, не сохраняем ничего
        return

    # Если выбрано существующее имя, делаем его активным
    success = save_current_player(selected_name)

    if success:
        # Перезапускаем сцену меню, чтобы обновить отображение
        set_next_scene('menu')
        if root_window:
            root_window.destroy()
    else:
        tk.messagebox.showerror("Ошибка", "Не удалось сделать игрока активным.")


# ----------------- КОНСТРУКТОРЫ СЕКЦИЙ -----------------
def setup_player_selection_section(parent_frame, team_name):
    """Отображает секцию выбора игрока."""
    global player_name_var

    # --- 1. ПОЛУЧАЕМ ДАННЫЕ ---
    current_player_name = get_current_player_name()
    all_players = get_all_player_names()

    is_new_player_mode = not bool(all_players)  # Режим добавления, если список пуст

    # 1. Отображение имени команды
    ttk.Label(
        parent_frame,
        text=f"АКТИВНАЯ КОМАНДА: {team_name}",
        font=("Arial", 16, "bold"),
        foreground="green"
    ).pack(pady=(20, 10))

    # 2. Создание фрейма для группировки
    player_frame = ttk.Frame(parent_frame)
    player_frame.pack(pady=20)

    # 3. Установка текста лейбла и списка значений

    values_list = []  # Список для Combobox
    button_text = "Сделать Активным"

    if is_new_player_mode:
        label_text = "Введите имя нового игрока:"
        initial_value = "Добавить нового игрока"  # Используем как приглашение
        color = "red"
        button_text = "Добавить Игрока"
    else:
        # Если игроки есть, добавляем их имена
        values_list.extend(all_players)

        # Добавляем специальную строку в конец списка!
        values_list.append("Добавить нового игрока")

        # Начальное значение - активный игрок
        initial_value = current_player_name if current_player_name else all_players[0]
        label_text = "Активный Игрок:"
        color = "black"

    # 4. Лейбл
    ttk.Label(
        player_frame,
        text=label_text,
        font=("Arial", 14)
    ).pack(side=tk.LEFT, padx=10)

    player_name_var = tk.StringVar(value=initial_value)

    # Определяем, какой виджет использовать: Entry или Combobox
    if is_new_player_mode:
        # --- Режим Добавления (Entry), если список пуст ---
        entry = ttk.Entry(
            player_frame,
            textvariable=player_name_var,
            width=25,
            font=("Arial", 14),
            foreground=color
        )
        entry.pack(side=tk.LEFT, padx=10)

        # Обработчик для очистки поля "Добавить нового игрока"
        def clear_on_focus(event):
            if player_name_var.get() == "Добавить нового игрока":
                player_name_var.set("")
                entry.config(foreground="black")

        entry.bind("<FocusIn>", clear_on_focus)

    else:
        # --- Режим Выбора (Combobox) ---
        entry = ttk.Combobox(
            player_frame,
            textvariable=player_name_var,
            values=values_list,  # Используем список со строкой-приглашением
            width=23,
            font=("Arial", 14)
        )
        entry.pack(side=tk.LEFT, padx=10)

        # Привязка события выбора
        entry.bind("<<ComboboxSelected>>", handle_combobox_selection)

        # Установим начальное значение
        entry.set(initial_value)

        # 5. КНОПКА "Выбрать/Добавить"
    # Кнопка нужна всегда в режиме Entry (для сохранения),
    # и нужна в режиме Combobox, если пользователь ВВЕЛ имя, а не выбрал

    ttk.Button(
        player_frame,
        text=button_text,
        command=handle_player_selection  # Используем общий обработчик для сохранения/активации
    ).pack(side=tk.LEFT, padx=10)


def show_menu():
    """Создает и отображает главное меню с логикой проверки команды."""
    global root_window, current_team_name

    # --- 1. ПРОВЕРКА НАЛИЧИЯ КОМАНДЫ ---
    current_team_name = get_team_name()  # Используем team_manager

    root_window = tk.Tk()
    root_window.title(WINDOW_TITLE + " - Главное Меню")

    # Центрирование окна (код без изменений)
    screen_width = root_window.winfo_screenwidth()
    screen_height = root_window.winfo_screenheight()
    x = (screen_width / 2) - (WINDOW_WIDTH / 2)
    y = (screen_height / 2) - (WINDOW_HEIGHT / 2)
    root_window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{int(x)}+{int(y)}')
    root_window.resizable(False, False)

    main_frame = ttk.Frame(root_window, padding="40")
    main_frame.pack(fill='both', expand=True)

    # 2. Заголовок
    ttk.Label(
        main_frame,
        text="Главное Меню Игры",
        font=("Arial", 28, "bold")
    ).pack(pady=30)

    # --- 3. УСЛОВНАЯ СЕКЦИЯ ИДЕНТИФИКАЦИИ ---

    id_frame = ttk.Frame(main_frame)
    id_frame.pack(pady=20)

    if current_team_name:
        # Если команда ЕСТЬ: показываем ее название и поле выбора игрока
        setup_player_selection_section(id_frame, current_team_name)
    else:
        # Если команды НЕТ: показываем поле для ее создания
        setup_team_creation_section(id_frame)

    # --- 4. Секция Кнопок (без изменений, кроме проверки в close_scene_and_switch) ---

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=40)

    # 1. Начать Игру
    ttk.Button(
        button_frame,
        text="Начать Игру (4x4)",
        command=lambda: close_scene_and_switch('game'),
        width=25
    ).pack(pady=15)

    # 2. Таблица Рекордов
    ttk.Button(
        button_frame,
        text="Таблица Рекордов",
        command=lambda: close_scene_and_switch('results'),
        width=25
    ).pack(pady=15)

    # 3. Настройки
    ttk.Button(
        button_frame,
        text="Настройки (WIP)",
        command=lambda: print("Кнопка 'Настройки' нажата."),
        width=25
    ).pack(pady=15)

    # 4. Выход
    ttk.Button(
        button_frame,
        text="Выход",
        command=lambda: close_scene_and_switch('exit'),
        width=25
    ).pack(pady=30)

    root_window.mainloop()

    return get_next_scene()