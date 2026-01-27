# game/game_loop.py
# game/game_loop.py

import pygame
import sys
import math
from tkinter import messagebox

# Импорты внутренней логики
from game.logic import shuffle_board, make_move, is_tile_in_place, calculate_e
from game.state import get_state, init_game_state, set_state
from settings.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE

# --- КОНСТАНТЫ ОКНА И ДИЗАЙНА ---
FPS = 60
INFO_PANEL_HEIGHT = 60
INDICATOR_HEIGHT = 60
INDICATOR_PADDING_X = 10
INDICATOR_INNER_WIDTH = WINDOW_WIDTH - 2 * INDICATOR_PADDING_X

BOARD_AREA_SIZE = 600  # Фиксированная область 600x600 для поля
BOARD_AREA_START_Y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT

# --- ЦВЕТА ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (220, 220, 220)
TILE_COLOR = (150, 150, 255)
TILE_COLOR_SOLVED = (100, 255, 100)
TILE_BORDER = 2


# ----------------------------------------------------
# ФУНКЦИИ ОТРИСОВКИ
# ----------------------------------------------------

def draw_info_panel(screen, state, font):
    """Отрисовывает верхнюю информационную панель (Зона А)."""
    panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, INFO_PANEL_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 255), panel_rect)
    pygame.draw.line(screen, BLACK, (0, INFO_PANEL_HEIGHT), (WINDOW_WIDTH, INFO_PANEL_HEIGHT), 2)

    # Используем 'coeff_k' для отображения, так как этот ключ в твоем стейте
    info_data = [
        f"Игрок: {state['player_name']}",
        f"Ширина: {state['board_w']}",
        f"Высота: {state['board_h']}",
        f"Время: {state.get('time_elapsed', 0.0):.0f} сек.",
        f"Ходов: {state.get('moves_count', 0)}",
        f"E: {state.get('coeff_k', 0):.1f}"
    ]

    num_items = len(info_data)
    item_width = WINDOW_WIDTH // num_items
    is_playing = state.get('is_playing', False)

    # Подсветка Таймера, если игра не начата
    if not is_playing:
        timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)
        pygame.draw.rect(screen, (255, 230, 150), timer_rect, 0)
        pygame.draw.rect(screen, (200, 100, 0), timer_rect, 3)

    for i, text in enumerate(info_data):
        x_start = i * item_width
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=(x_start + item_width // 2, INFO_PANEL_HEIGHT // 2))
        screen.blit(text_surf, text_rect)
        if i < num_items - 1:
            pygame.draw.line(screen, BLACK, (x_start + item_width, 0), (x_start + item_width, INFO_PANEL_HEIGHT), 1)


def draw_indicator_panel(screen, state):
    """Отрисовывает индикатор эффективности (Зона Б)."""
    rect = pygame.Rect(0, INFO_PANEL_HEIGHT, WINDOW_WIDTH, INDICATOR_HEIGHT)
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.line(screen, BLACK, (0, BOARD_AREA_START_Y), (WINDOW_WIDTH, BOARD_AREA_START_Y), 2)

    font = pygame.font.Font(None, 36)

    # Расчет полоски индикатора (на основе шкалы 0-1000)
    e_value = state.get('coeff_k', 0.0)
    normalized_e = min(1.0, max(0.0, e_value / 1000.0))
    indicator_width = normalized_e * INDICATOR_INNER_WIDTH

    # Цвет: от красного (0) к зеленому (1000)
    color = (int(255 * (1 - normalized_e)), int(255 * normalized_e), 0)

    # Рисуем полосу
    k_rect = pygame.Rect(INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, indicator_width, INDICATOR_HEIGHT - 20)
    if state.get('is_playing', False):
        pygame.draw.rect(screen, color, k_rect)

    pygame.draw.rect(screen, BLACK,
                     (INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, INDICATOR_INNER_WIDTH, INDICATOR_HEIGHT - 20), 1)

    # Текст значения
    current_e_text = f"Эффективность: {e_value:.1f} / 1000"
    text_surf = font.render(current_e_text, True, BLACK)
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, INFO_PANEL_HEIGHT + INDICATOR_HEIGHT // 2))
    screen.blit(text_surf, text_rect)


def draw_board(screen, state, TILE_SIZE, start_x, start_y, font):
    """Отрисовывает игровое поле (Зона В)."""
    board = state['tiles']
    board_w = state['board_w']
    board_h = state['board_h']

    # Рамка поля
    full_board_rect = pygame.Rect(start_x - TILE_BORDER, start_y - TILE_BORDER,
                                  (TILE_SIZE * board_w) + TILE_BORDER * 2,
                                  (TILE_SIZE * board_h) + TILE_BORDER * 2)
    pygame.draw.rect(screen, BLACK, full_board_rect, TILE_BORDER)

    for row in range(board_h):
        for col in range(board_w):
            tile_value = board[row][col]
            x, y = start_x + col * TILE_SIZE, start_y + row * TILE_SIZE

            if tile_value != 0:
                # Цвет зависит от того, на своем ли месте плитка
                color = TILE_COLOR_SOLVED if is_tile_in_place(tile_value, row, col, board_w, board_h) else TILE_COLOR

                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)

                text_surf = font.render(str(tile_value), True, BLACK)
                text_rect = text_surf.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text_surf, text_rect)
            else:
                pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)


# ----------------------------------------------------
# ГЛАВНЫЙ ЦИКЛ
# ----------------------------------------------------

def start_game_loop(menu_root, player_name, board_w, board_h):
    init_game_state(player_name, board_w, board_h)
    menu_root.withdraw()

    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
    except Exception as e:
        messagebox.showerror("Ошибка Pygame", f"Критический сбой: {e}")
        pygame.quit()
        menu_root.deiconify()
        return

    # Расчет размеров
    TILE_SIZE = min(BOARD_AREA_SIZE // board_w, BOARD_AREA_SIZE // board_h)
    BOARD_START_X = (WINDOW_WIDTH - (TILE_SIZE * board_w)) // 2
    BOARD_START_Y = BOARD_AREA_START_Y + (BOARD_AREA_SIZE - (TILE_SIZE * board_h)) // 2

    last_time = pygame.time.get_ticks()
    running = True

    while running:
        # Расчет времени
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time

        state = get_state()
        is_playing = state.get('is_playing', False)

        # --- ОБНОВЛЕНИЕ СОСТОЯНИЯ ---
        if is_playing:
            # Обновляем время
            new_time = state.get('time_elapsed', 0.0) + delta_time
            set_state('time_elapsed', new_time)

            # Обновляем коэффициент эффективности (ТОТ САМЫЙ МОТОР)
            set_state('coeff_k', calculate_e())

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                # Клик по таймеру (Старт)
                if not is_playing:
                    item_width = WINDOW_WIDTH // 6
                    timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)
                    if timer_rect.collidepoint(mouse_x, mouse_y):
                        shuffle_board()
                        last_time = pygame.time.get_ticks()

                # Клик по доске (Ход)
                elif is_playing:
                    if mouse_x >= BOARD_START_X and mouse_y >= BOARD_START_Y:
                        col = (mouse_x - BOARD_START_X) // TILE_SIZE
                        row = (mouse_y - BOARD_START_Y) // TILE_SIZE
                        if 0 <= row < board_h and 0 <= col < board_w:
                            make_move(row, col)

        # Отрисовка
        screen.fill(BACKGROUND_COLOR)
        draw_info_panel(screen, state, font)
        draw_indicator_panel(screen, state)
        draw_board(screen, state, TILE_SIZE, BOARD_START_X, BOARD_START_Y, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


# game/game_loop.py

import pygame
import sys
import math
from tkinter import messagebox

# Импорты внутренней логики
from game.logic import shuffle_board, make_move, is_tile_in_place, calculate_e
from game.state import get_state, init_game_state, set_state
from settings.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE

# --- КОНСТАНТЫ ОКНА И ДИЗАЙНА ---
FPS = 60
INFO_PANEL_HEIGHT = 60
INDICATOR_HEIGHT = 60
INDICATOR_PADDING_X = 10
INDICATOR_INNER_WIDTH = WINDOW_WIDTH - 2 * INDICATOR_PADDING_X

BOARD_AREA_SIZE = 600  # Фиксированная область 600x600 для поля
BOARD_AREA_START_Y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT

# --- ЦВЕТА ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (220, 220, 220)
TILE_COLOR = (150, 150, 255)
TILE_COLOR_SOLVED = (100, 255, 100)
TILE_BORDER = 2


# ----------------------------------------------------
# ФУНКЦИИ ОТРИСОВКИ
# ----------------------------------------------------

def draw_info_panel(screen, state, font):
    """Отрисовывает верхнюю информационную панель (Зона А)."""
    panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, INFO_PANEL_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 255), panel_rect)
    pygame.draw.line(screen, BLACK, (0, INFO_PANEL_HEIGHT), (WINDOW_WIDTH, INFO_PANEL_HEIGHT), 2)

    # Используем 'coeff_k' для отображения, так как этот ключ в твоем стейте
    info_data = [
        f"Игрок: {state['player_name']}",
        f"Ширина: {state['board_w']}",
        f"Высота: {state['board_h']}",
        f"Время: {state.get('time_elapsed', 0.0):.0f} сек.",
        f"Ходов: {state.get('moves_count', 0)}",
        f"E: {state.get('coeff_k', 0):.1f}"
    ]

    num_items = len(info_data)
    item_width = WINDOW_WIDTH // num_items
    is_playing = state.get('is_playing', False)

    # Подсветка Таймера, если игра не начата
    if not is_playing:
        timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)
        pygame.draw.rect(screen, (255, 230, 150), timer_rect, 0)
        pygame.draw.rect(screen, (200, 100, 0), timer_rect, 3)

    for i, text in enumerate(info_data):
        x_start = i * item_width
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=(x_start + item_width // 2, INFO_PANEL_HEIGHT // 2))
        screen.blit(text_surf, text_rect)
        if i < num_items - 1:
            pygame.draw.line(screen, BLACK, (x_start + item_width, 0), (x_start + item_width, INFO_PANEL_HEIGHT), 1)


def draw_indicator_panel(screen, state):
    """Отрисовывает индикатор эффективности (Зона Б)."""
    rect = pygame.Rect(0, INFO_PANEL_HEIGHT, WINDOW_WIDTH, INDICATOR_HEIGHT)
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.line(screen, BLACK, (0, BOARD_AREA_START_Y), (WINDOW_WIDTH, BOARD_AREA_START_Y), 2)

    font = pygame.font.Font(None, 36)

    # Расчет полоски индикатора (на основе шкалы 0-1000)
    e_value = state.get('coeff_k', 0.0)
    normalized_e = min(1.0, max(0.0, e_value / 1000.0))
    indicator_width = normalized_e * INDICATOR_INNER_WIDTH

    # Цвет: от красного (0) к зеленому (1000)
    color = (int(255 * (1 - normalized_e)), int(255 * normalized_e), 0)

    # Рисуем полосу
    k_rect = pygame.Rect(INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, indicator_width, INDICATOR_HEIGHT - 20)
    if state.get('is_playing', False):
        pygame.draw.rect(screen, color, k_rect)

    pygame.draw.rect(screen, BLACK,
                     (INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, INDICATOR_INNER_WIDTH, INDICATOR_HEIGHT - 20), 1)

    # Текст значения
    current_e_text = f"Эффективность: {e_value:.1f} / 1000"
    text_surf = font.render(current_e_text, True, BLACK)
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, INFO_PANEL_HEIGHT + INDICATOR_HEIGHT // 2))
    screen.blit(text_surf, text_rect)


def draw_board(screen, state, TILE_SIZE, start_x, start_y, font):
    """Отрисовывает игровое поле (Зона В)."""
    board = state['tiles']
    board_w = state['board_w']
    board_h = state['board_h']

    # Рамка поля
    full_board_rect = pygame.Rect(start_x - TILE_BORDER, start_y - TILE_BORDER,
                                  (TILE_SIZE * board_w) + TILE_BORDER * 2,
                                  (TILE_SIZE * board_h) + TILE_BORDER * 2)
    pygame.draw.rect(screen, BLACK, full_board_rect, TILE_BORDER)

    for row in range(board_h):
        for col in range(board_w):
            tile_value = board[row][col]
            x, y = start_x + col * TILE_SIZE, start_y + row * TILE_SIZE

            if tile_value != 0:
                # Цвет зависит от того, на своем ли месте плитка
                color = TILE_COLOR_SOLVED if is_tile_in_place(tile_value, row, col, board_w, board_h) else TILE_COLOR

                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)

                text_surf = font.render(str(tile_value), True, BLACK)
                text_rect = text_surf.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text_surf, text_rect)
            else:
                pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)


# ----------------------------------------------------
# ГЛАВНЫЙ ЦИКЛ
# ----------------------------------------------------

def start_game_loop(menu_root, player_name, board_w, board_h):
    init_game_state(player_name, board_w, board_h)
    menu_root.withdraw()

    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
    except Exception as e:
        messagebox.showerror("Ошибка Pygame", f"Критический сбой: {e}")
        pygame.quit()
        menu_root.deiconify()
        return

    # Расчет размеров
    TILE_SIZE = min(BOARD_AREA_SIZE // board_w, BOARD_AREA_SIZE // board_h)
    BOARD_START_X = (WINDOW_WIDTH - (TILE_SIZE * board_w)) // 2
    BOARD_START_Y = BOARD_AREA_START_Y + (BOARD_AREA_SIZE - (TILE_SIZE * board_h)) // 2

    last_time = pygame.time.get_ticks()
    running = True

    while running:
        # Расчет времени
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time

        state = get_state()
        is_playing = state.get('is_playing', False)

        # --- ОБНОВЛЕНИЕ СОСТОЯНИЯ ---
        if is_playing:
            # Обновляем время
            new_time = state.get('time_elapsed', 0.0) + delta_time
            set_state('time_elapsed', new_time)

            # Обновляем коэффициент эффективности (ТОТ САМЫЙ МОТОР)
            set_state('coeff_k', calculate_e())

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                # Клик по таймеру (Старт)
                if not is_playing:
                    item_width = WINDOW_WIDTH // 6
                    timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)
                    if timer_rect.collidepoint(mouse_x, mouse_y):
                        shuffle_board()
                        last_time = pygame.time.get_ticks()

                # Клик по доске (Ход)
                elif is_playing:
                    if mouse_x >= BOARD_START_X and mouse_y >= BOARD_START_Y:
                        col = (mouse_x - BOARD_START_X) // TILE_SIZE
                        row = (mouse_y - BOARD_START_Y) // TILE_SIZE
                        if 0 <= row < board_h and 0 <= col < board_w:
                            make_move(row, col)

        # Отрисовка
        screen.fill(BACKGROUND_COLOR)
        draw_info_panel(screen, state, font)
        draw_indicator_panel(screen, state)
        draw_board(screen, state, TILE_SIZE, BOARD_START_X, BOARD_START_Y, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
