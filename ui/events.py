# ui/events.py

import pygame
import random

from ui.elements import (
    UI_WIDTH_MENU,
    MENU_ELEMENTS,
    DROPDOWN_ELEMENTS,
)

from players.manager import (
    load_players,
    add_player,
    get_active_player,
    set_active_player,
    delete_active_player,   # ← добавили

)
from settings.manager import (
    load_settings,
    update_settings,
)

# --- UI state ---
selected_input = None
input_width = ""
input_height = ""

adding_player = False
input_player_name = ""

dropdown_open = False
scroll_offset = 0

w_mode = None   # None / "random" / "set"
h_mode = None   # None / "random" / "set"

game_started = False

# локально кэшируем активное имя
active_name = get_active_player() or ""

# загружаем настройки при старте
_settings = load_settings()
w_mode = _settings.get("width_mode", "random")
h_mode = _settings.get("height_mode", "random")
input_width = str(_settings.get("width_value", 6)) if w_mode == "set" else ""
input_height = str(_settings.get("height_value", 6)) if h_mode == "set" else ""


def _hit_index(pos_y, rect_top, scroll, item_h=40, pad=5):
    """Вернуть (index, within_item) по клику в список, учитывая прокрутку и промежутки."""
    step = item_h + pad
    local_y = (pos_y - rect_top) + scroll
    if local_y < 0:
        return (-1, False)
    index = local_y // step
    within_item = (local_y % step) < item_h
    return (index, within_item)


def handle_mouse_click(pos, state):
    global selected_input, adding_player, dropdown_open, scroll_offset
    global input_player_name, w_mode, h_mode, game_started, active_name
    global input_width, input_height
    global selected_input, team_name

    # --- Поле "Команда" ---
    if MENU_ELEMENTS["team_name"]["rect"].collidepoint(pos):
        if not state.team_confirmed:  # можно вводить только если команда ещё не подтверждена
            print(">>> Активировано поле 'Команда'")
            state.selected_input = "team_name"
        else:
            print(f">>> Команда уже задана: {state.team_name}")
            state.selected_input = None
        return True

    # --- Поле имени игрока ---
    if DROPDOWN_ELEMENTS["player_name"]["rect"].collidepoint(pos):
        print(">>> Нажата кнопка 'Имя игрока'")
        dropdown_open = not dropdown_open  # открываем/закрываем список игроков
        state.selected_input = "player_dropdown"  # фиксируем, что активен dropdown игроков
        state.scroll_offset = 0  # сбрасываем прокрутку
        return True

    # --- Поле ширины ---
    if MENU_ELEMENTS["width"]["rect"].collidepoint(pos):
        dropdown_open = True
        state.selected_input = "width_mode"
        state.scroll_offset = 0
        return True

    # --- Поле высоты ---
    if MENU_ELEMENTS["height"]["rect"].collidepoint(pos):
        dropdown_open = True
        state.selected_input = "height_mode"
        state.scroll_offset = 0
        return True

    # --- Dropdown ---
    if dropdown_open:
        # Список игроков
        if selected_input == "player_dropdown" and DROPDOWN_ELEMENTS["player_name"]["rect"].collidepoint(pos):
            players = load_players()
            names = [p["name"] for p in players] + ["Новый игрок"]

            index, within_item = _hit_index(pos[1], DROPDOWN_ELEMENTS["player_name"]["rect"].y, scroll_offset)
            if within_item and 0 <= index < len(names):
                name = names[index]
                if name == "Новый игрок":
                    adding_player = True
                    selected_input = "player_name"
                    input_player_name = ""
                else:
                    set_active_player(name)
                    active_name = name
                    adding_player = False
                    selected_input = None

                dropdown_open = False
                scroll_offset = 0
                return True

            dropdown_open = False
            scroll_offset = 0
            return True

            dropdown_open = False
            scroll_offset = 0
            return True

        # Список режима ширины
        elif selected_input == "width_mode" and WIDTH_DROPDOWN_RECT.collidepoint(pos):
            options = ["Случайная", "Задать"]
            index, within_item = _hit_index(pos[1], WIDTH_DROPDOWN_RECT.y, scroll_offset)
            if within_item and 0 <= index < len(options):
                choice = options[index]
                if choice == "Случайная":
                    w_mode = "random"
                    input_width = ""
                    selected_input = None
                else:
                    w_mode = "set"
                    input_width = ""
                    selected_input = "width"

            dropdown_open = False
            scroll_offset = 0
            return True

        # Список режима высоты
        elif selected_input == "height_mode" and HEIGHT_DROPDOWN_RECT.collidepoint(pos):
            options = ["Случайная", "Задать"]
            index, within_item = _hit_index(pos[1], HEIGHT_DROPDOWN_RECT.y, scroll_offset)
            if within_item and 0 <= index < len(options):
                choice = options[index]
                if choice == "Случайная":
                    h_mode = "random"
                    input_height = ""
                    selected_input = None
                else:
                    h_mode = "set"
                    input_height = ""
                    selected_input = "height"

            dropdown_open = False
            scroll_offset = 0
            return True

    # если был открыт dropdown, но кликнули вне — закрыть
    dropdown_open = False
    scroll_offset = 0



    # --- Кнопка "Старт" ---
    if MENU_ELEMENTS["start"]["rect"].collidepoint(pos):
        new_w = 6
        new_h = 6

        if w_mode == "random":
            new_w = random.randint(4, 10)
        elif w_mode == "set" and input_width.isdigit():
            val = int(input_width)
            if 4 <= val <= 10:
                new_w = val

        if h_mode == "random":
            new_h = random.randint(4, 10)
        elif h_mode == "set" and input_height.isdigit():
            val = int(input_height)
            if 4 <= val <= 10:
                new_h = val

        state.resize_board(new_w, new_h)
        state.start_time = pygame.time.get_ticks()
        game_started = True

        # сохраняем настройки при старте
        update_settings(w_mode, h_mode, new_w, new_h)
        return True

    # --- Клик по игровому полю (только если игра начата) ---
    if game_started:
        game_x = pos[0] - UI_WIDTH_MENU
        game_y = pos[1]
        if game_x >= 0:
            tile_x = game_x // state.tile_w
            tile_y = game_y // state.tile_h
            state.try_move(tile_x, tile_y)
            return True

    return False


def handle_mouse_wheel(event):
    global scroll_offset

    if not dropdown_open:
        return False
    if event.button not in (4, 5):
        return False

    # длина списка и видимая высота
    if selected_input == "player_dropdown":
        names_count = len(load_players()) + 1  # + "Новый игрок"
        visible_h = DROPDOWN_RECT.height
    elif selected_input == "width_mode":
        names_count = 2
        visible_h = WIDTH_DROPDOWN_RECT.height
    elif selected_input == "height_mode":
        names_count = 2
        visible_h = HEIGHT_DROPDOWN_RECT.height
    else:
        return False

    item_h = 40
    pad = 5
    step = item_h + pad

    full_h = names_count * step
    max_offset = max(0, full_h - visible_h)

    if event.button == 4:
        scroll_offset = max(0, scroll_offset - 20)
    elif event.button == 5:
        scroll_offset = min(max_offset, scroll_offset + 20)

    return True


def handle_text_input(event, state):
    # Ввод названия команды (только если она ещё не подтверждена)
    if state.selected_input == "team_name" and not state.team_confirmed:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            from settings.manager import save_team
            save_team(state.team_name)
            state.team_confirmed = True   # ← команда зафиксирована
            print(f">>> Команда создана: {state.team_name}")
            state.selected_input = None
            return True

        if event.key == pygame.K_ESCAPE:
            state.selected_input = None
            state.team_name = ""
            return True

        if event.key == pygame.K_BACKSPACE:
            state.team_name = state.team_name[:-1]
            return True

        char = event.unicode
        if char and not char.isspace():
            state.team_name += char
            print(">>> Введено:", state.team_name)
            return True



    # Режим ввода нового игрока
    if state.adding_player:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            name = state.input_player_name.strip()
            if name:
                add_player(name)
                set_active_player(name)
                state.active_name = name
            state.adding_player = False
            state.selected_input = None
            state.input_player_name = ""
            return True

        if event.key == pygame.K_ESCAPE:
            state.adding_player = False
            state.selected_input = None
            state.input_player_name = ""
            return True

        if event.key == pygame.K_BACKSPACE:
            state.input_player_name = state.input_player_name[:-1]
            return True

        char = event.unicode
        if char and not char.isspace():
            state.input_player_name += char
            return True

    return False


def handle_numeric_input(event, state):
    # пример: ввод числовых значений ширины/высоты
    if state.selected_input == "width":
        if event.key == pygame.K_BACKSPACE:
            state.input_width = state.input_width[:-1]
            return True
        char = event.unicode
        if char.isdigit():
            state.input_width += char
            return True

    if state.selected_input == "height":
        if event.key == pygame.K_BACKSPACE:
            state.input_height = state.input_height[:-1]
            return True
        char = event.unicode
        if char.isdigit():
            state.input_height += char
            return True

    return False


def handle_events(state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # колесо мыши: 4 (вверх), 5 (вниз)
            if event.button in (4, 5):
                if handle_mouse_wheel(event):
                    continue
            else:
                if handle_mouse_click(event.pos, state):
                    continue

        if event.type == pygame.KEYDOWN:
            if handle_text_input(event, state):
                continue
            if handle_numeric_input(event, state):  # ← исправлено
                continue
            if event.key == pygame.K_DELETE:
                from players.manager import delete_active_player
                deleted = delete_active_player()
                if deleted:
                    print(">>> Активный игрок удалён")
                continue

    return True
