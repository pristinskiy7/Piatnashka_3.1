# display/display_menu.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # <--- ДОБАВЬТЕ ЭТУ СТРОКУ
from ui.elements import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from ui.handler_tkinter import set_next_scene, get_next_scene
from players.manager import get_current_player_name, save_current_player, get_all_player_names, delete_player # <--- ДОБАВЛЕН ИМПОРТ
from players.team_manager import get_team_name, save_team_name  # <--- НОВЫЙ ИМПОРТ
# Новые импорты настроек
from settings.preferences import get_board_preferences, set_board_preferences, MIN_SIZE, MAX_SIZE,DEFAULT_SIZE

# Глобальные переменные для управления состоянием комбобоксов
size_w_var = None
size_h_var = None
w_combobox = None
h_combobox = None


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


# display/display_menu.py

# ... (после handle_combobox_selection) ...

def handle_player_delete():
    """Обработчик кнопки удаления активного игрока."""
    global root_window

    player_name = get_current_player_name()

    if not player_name:
        messagebox.showwarning("Предупреждение", "Нет активного игрока для удаления.")
        return

    # Запрос подтверждения удаления
    confirm = messagebox.askyesno(  # <--- Исправлено: messagebox
        "Подтверждение удаления",
        f"Вы действительно хотите удалить игрока '{player_name}'? Все его результаты будут утеряны!"
    )

    if confirm:
        success = delete_player(player_name)

        if success:
            messagebox.showinfo("Успех", f"Игрок '{player_name}' успешно удален.")  # <--- Исправлено: messagebox

            # Перезапускаем сцену меню, чтобы обновить отображение
            set_next_scene('menu')
            if root_window:
                root_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить игрока.")  # <--- Исправлено: messagebox
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

    # --- НОВАЯ СЕКЦИЯ: КНОПКА УДАЛЕНИЯ ---
    # Показываем кнопку удаления, только если есть активный игрок
    if current_player_name:
        ttk.Button(
            player_frame,
            text="Удалить Игрока",
            command=handle_player_delete,
            style='Danger.TButton'  # Предполагая, что у вас есть такой стиль для красного цвета
        ).pack(side=tk.LEFT, padx=10)


# display/display_menu.py

# ... (после других вспомогательных функций) ...

def _validate_and_save_size(dimension_var, is_width):
    """Общая функция для валидации ручного ввода и сохранения W или H."""

    # 1. Загружаем текущие настройки для сброса в случае ошибки
    current_prefs = get_board_preferences()

    value_str = dimension_var.get().strip()
    dimension_name = "Ширина (W)" if is_width else "Высота (H)"

    # 2. Проверяем режим "RANDOM"
    if value_str.upper() == "RANDOM":
        w = "RANDOM" if is_width else current_prefs['w']
        h = current_prefs['h'] if is_width else "RANDOM"
        set_board_preferences(w, h)
        return True

    # 3. Валидация числового ввода
    try:
        value_int = int(value_str)
        if MIN_SIZE <= value_int <= MAX_SIZE:
            # Валидное число, сохраняем
            w = value_int if is_width else current_prefs['w']
            h = current_prefs['h'] if is_width else value_int
            set_board_preferences(w, h)
            print(f"ЛОГ: Размер {dimension_name} сохранен: {value_int}.")
            return True
        else:
            # Невалидный диапазон: сбрасываем значение в поле
            messagebox.showerror("Ошибка ввода",
                                 f"Размер {dimension_name} должен быть целым числом от {MIN_SIZE} до {MAX_SIZE}.")
            # Сбрасываем поле на предыдущее валидное значение (или 4)
            prev_val = current_prefs['w'] if is_width else current_prefs['h']
            if prev_val == "RANDOM":
                dimension_var.set(str(DEFAULT_SIZE))  # Используем 4, если предыдущее было RANDOM
            else:
                dimension_var.set(str(prev_val))
            return False

    except ValueError:
        # Не число: сбрасываем значение в поле
        messagebox.showerror("Ошибка ввода", f"Размер {dimension_name} должен быть целым числом.")
        # Сбрасываем поле на предыдущее валидное значение (или 4)
        prev_val = current_prefs['w'] if is_width else current_prefs['h']
        if prev_val == "RANDOM":
            dimension_var.set(str(DEFAULT_SIZE))
        else:
            dimension_var.set(str(prev_val))
        return False


def _handle_mode_change(combobox, dimension_var, is_width, event):
    """Обработчик выбора 'Выбрать'/'Случайная' из выпадающего списка."""
    selected_mode = combobox.get()

    if selected_mode == "Случайная":
        # Устанавливаем режим RANDOM
        dimension_var.set("RANDOM")
        combobox.config(state="readonly")  # Запрещаем ручной ввод
        _validate_and_save_size(dimension_var, is_width)  # Сохраняем немедленно

    elif selected_mode == "Выбрать":
        # Возвращаем поле в режим ручного ввода
        current_prefs = get_board_preferences()
        last_valid_value = current_prefs['w'] if is_width else current_prefs['h']

        # Если последнее сохраненное значение было RANDOM, ставим дефолт
        if last_valid_value == "RANDOM":
            last_valid_value = str(MIN_SIZE)

        dimension_var.set(str(last_valid_value))
        combobox.config(state="normal")  # Разрешаем ручной ввод

    # Сбрасываем текст комбобокса, чтобы он показывал текущее значение (RANDOM или число)
    combobox.set(dimension_var.get())


# display/display_menu.py

# ... (после _handle_mode_change) ...

def setup_size_selection_section(container_frame):
    """Отрисовывает секцию выбора размера поля (W и H)."""
    global size_w_var, size_h_var, w_combobox, h_combobox

    # 1. Загружаем текущие настройки
    current_prefs = get_board_preferences()
    current_w = current_prefs['w']
    current_h = current_prefs['h']

    # 2. Создаем заголовок секции
    size_label = tk.Label(container_frame, text="📏 Настройки размера поля (4-10):", font=("Arial", 12, "bold"),
                          bg="#E0E0E0")
    size_label.pack(pady=(10, 5))

    # 3. Фрейм для размещения W и H рядом
    size_frame = tk.Frame(container_frame, bg="#E0E0E0")
    size_frame.pack(pady=5)

    # Настройки Combobox
    modes = ["Выбрать", "Случайная"]

    # --- ШИРИНА (W) ---
    tk.Label(size_frame, text="Ширина (W):", bg="#E0E0E0", font=("Arial", 10)).pack(side='left', padx=(20, 5))

    # Инициализация переменных и состояния
    initial_w_value = str(current_w)
    initial_w_state = "readonly" if current_w == "RANDOM" else "normal"

    if size_w_var is None:
        size_w_var = tk.StringVar(size_frame, value=initial_w_value)

    w_combobox = ttk.Combobox(
        size_frame,
        textvariable=size_w_var,
        values=modes,
        state=initial_w_state,
        width=10,
        justify='center',
        font=("Arial", 11)
    )
    w_combobox.pack(side='left', padx=(0, 10))

    # Обработчики событий
    w_combobox.bind('<<ComboboxSelected>>', lambda event: _handle_mode_change(w_combobox, size_w_var, True, event))
    w_combobox.bind('<FocusOut>', lambda event: _validate_and_save_size(size_w_var, True))

    # --- ВЫСОТА (H) ---
    tk.Label(size_frame, text="Высота (H):", bg="#E0E0E0", font=("Arial", 10)).pack(side='left', padx=(10, 5))

    # Инициализация переменных и состояния
    initial_h_value = str(current_h)
    initial_h_state = "readonly" if current_h == "RANDOM" else "normal"

    if size_h_var is None:
        size_h_var = tk.StringVar(size_frame, value=initial_h_value)

    h_combobox = ttk.Combobox(
        size_frame,
        textvariable=size_h_var,
        values=modes,
        state=initial_h_state,
        width=10,
        justify='center',
        font=("Arial", 11)
    )
    h_combobox.pack(side='left', padx=(0, 20))

    # Обработчики событий
    h_combobox.bind('<<ComboboxSelected>>', lambda event: _handle_mode_change(h_combobox, size_h_var, False, event))
    h_combobox.bind('<FocusOut>', lambda event: _validate_and_save_size(size_h_var, False))

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
        # ------------------- 2. СЕКЦИЯ ВЫБОРА ИГРОКА -------------------
        # Этот вызов должен остаться!
        setup_player_selection_section(id_frame, current_team_name)

        # ------------------- 3. СЕКЦИЯ ВЫБОРА РАЗМЕРА ПОЛЯ -------------------
        # ЭТОТ ВЫЗОВ МЫ ДОБАВЛЯЕМ
        setup_size_selection_section(id_frame)
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