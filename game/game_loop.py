# game/game_loop.py

import pygame
import sys
import tkinter as tk
from tkinter import messagebox

# Импорт модуля состояния, который хранит текущие W, H и имя игрока
from game.state import get_state, init_game_state

# --- КОНСТАНТЫ ОКНА И ДИЗАЙНА ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GAME_TITLE = "Пятнашка: Игра началась"
FPS = 60

# --- РАЗМЕРЫ ЗОН ---
INFO_PANEL_HEIGHT = 60
INDICATOR_HEIGHT = 60
BOARD_AREA_SIZE = 600  # Фиксированная область 600x600 для поля
BOARD_AREA_START_Y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT  # = 120

# --- ЦВЕТА И ОФОРМЛЕНИЕ ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (220, 220, 220)  # Светло-серый фон
TILE_COLOR = (150, 150, 255)  # Цвет плитки
TILE_BORDER = 2  # Ширина рамки
MARGIN = 10  # Отступ


# ----------------------------------------------------
# ФУНКЦИИ ОТРЕСОВКИ (РАСПОЛОЖЕНЫ НА ВЕРХНЕМ УРОВНЕ)
# ----------------------------------------------------

def draw_info_panel(screen, state, font):
    """Отрисовывает 6 информационных блоков в верхней части окна (Зона А)."""

    panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, INFO_PANEL_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 255), panel_rect)
    pygame.draw.line(screen, BLACK, (0, INFO_PANEL_HEIGHT), (WINDOW_WIDTH, INFO_PANEL_HEIGHT), 2)

    info_data = [
        f"Игрок: {state['player_name']}",
        f"Ширина: {state['board_w']}",
        f"Высота: {state['board_h']}",
        f"Время: {state.get('time_elapsed', 0):.0f} сек.",  # <-- ИСПРАВЛЕНО
        f"Ходов: {state.get('moves_count', 0)}",  # <-- ИСПРАВЛЕНО
        f"K: {state.get('coeff_k', 0):.2f}"
    ]

    num_items = len(info_data)
    item_width = WINDOW_WIDTH // num_items

    for i, text in enumerate(info_data):
        x_start = i * item_width

        # Отрисовка текста
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=(x_start + item_width // 2, INFO_PANEL_HEIGHT // 2))
        screen.blit(text_surf, text_rect)

        # Рисуем вертикальные разделители
        if i < num_items - 1:
            pygame.draw.line(screen, BLACK, (x_start + item_width, 0), (x_start + item_width, INFO_PANEL_HEIGHT), 1)


def draw_indicator_panel(screen, state):
    """Отрисовывает индикатор коэффициента K (Зона Б)."""
    rect = pygame.Rect(0, INFO_PANEL_HEIGHT, WINDOW_WIDTH, INDICATOR_HEIGHT)
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.line(screen, BLACK, (0, BOARD_AREA_START_Y), (WINDOW_WIDTH, BOARD_AREA_START_Y), 2)

    k_value = state.get('coeff_k', 0.0) # <-- Ключ 'coeff_k' теперь инициализирован в state.py

    font = pygame.font.Font(None, 24)
    text = f"Индикатор K ({k_value:.2f}) - Здесь будет визуализация"
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (10, INFO_PANEL_HEIGHT + INDICATOR_HEIGHT // 2 - 12))


def draw_board(screen, state, TILE_SIZE, start_x, start_y, font):
    """Отрисовывает игровое поле и плитки (Зона В)."""

    board = state['tiles']   # <-- ИСПОЛЬЗОВАТЬ 'tiles'
    board_w = state['board_w']
    board_h = state['board_h']

    # Рисуем общую рамку поля
    board_rect = pygame.Rect(start_x - TILE_BORDER, start_y - TILE_BORDER,
                             (TILE_SIZE * board_w) + TILE_BORDER * 2,
                             (TILE_SIZE * board_h) + TILE_BORDER * 2)
    pygame.draw.rect(screen, BLACK, board_rect, TILE_BORDER)

    for row in range(board_h):
        for col in range(board_w):
            tile_value = board[row][col]

            x = start_x + col * TILE_SIZE
            y = start_y + row * TILE_SIZE

            if tile_value != 0:
                # 1. Рисуем фоновую плитку
                pygame.draw.rect(screen, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))

                # 2. Рисуем рамку
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)

                # 3. Рисуем число
                text_size = TILE_SIZE // 3
                tile_font = pygame.font.Font(None, max(16, text_size))

                text_surf = tile_font.render(str(tile_value), True, BLACK)

                # Центрируем текст
                text_rect = text_surf.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text_surf, text_rect)

            else:
                # Пустая ячейка (0)
                pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)


# ----------------------------------------------------
# ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА
# ----------------------------------------------------

def start_game_loop(menu_root, player_name, board_w, board_h):
    # 1. Инициализируем состояние игры
    init_game_state(player_name, board_w, board_h)
    state = get_state()

    # 2. Скрываем окно меню Tkinter
    menu_root.withdraw()
    print(f"ЛОГ: Запуск Pygame для игрока {player_name} на поле {board_w}x{board_h}...")

    # --- КРИТИЧЕСКИЙ БЛОК ИНИЦИАЛИЗАЦИИ PYGAME ---
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)

    except pygame.error as e:
        print(f"--- 🛑 КРИТИЧЕСКАЯ ОШИБКА PYGAME: {e} ---")
        messagebox.showerror("Ошибка Pygame", f"Не удалось инициализировать Pygame/окно. Ошибка: {e}")
        pygame.quit()
        menu_root.deiconify()
        return
    except Exception as e:
        print(f"--- 🛑 НЕИЗВЕСТНАЯ ОШИБКА: {e} ---")
        messagebox.showerror("Неизвестная Ошибка", f"Произошла ошибка при старте игры: {e}")
        pygame.quit()
        menu_root.deiconify()
        return
    # --- КОНЕЦ КРИТИЧЕСКОГО БЛОКА ---

    # ----------------------------------------------------
    # БЛОК: РАСЧЕТ РАЗМЕРА ИГРОВОГО ПОЛЯ (600x600)
    # Переменные TILE_SIZE, BOARD_START_X/Y определяются здесь
    # ----------------------------------------------------

    available_size = BOARD_AREA_SIZE

    max_tile_size_w = available_size // board_w
    max_tile_size_h = available_size // board_h

    TILE_SIZE = min(max_tile_size_w, max_tile_size_h)

    BOARD_WIDTH_PX = TILE_SIZE * board_w
    BOARD_HEIGHT_PX = TILE_SIZE * board_h

    BOARD_START_X = (WINDOW_WIDTH - BOARD_WIDTH_PX) // 2
    BOARD_START_Y = BOARD_AREA_START_Y + (BOARD_AREA_SIZE - BOARD_HEIGHT_PX) // 2

    print(f"ЛОГ: Размер плитки: {TILE_SIZE}px. Поле начинается с ({BOARD_START_X}, {BOARD_START_Y}).")

    # ----------------------------------------------------
    # ГЛАВНЫЙ ЦИКЛ ИГРЫ
    # ----------------------------------------------------
    running = True
    while running:
        # Обновляем состояние в начале цикла
        state = get_state()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                    # TODO: Здесь будет обработка кликов мыши для перемещения плиток

        # ----------------------------------------------------
        # 6. Отрисовка
        # ----------------------------------------------------

        screen.fill(BACKGROUND_COLOR)

        # 1. Отрисовка Информационной Панели (Зона А)
        draw_info_panel(screen, state, font)

        # 2. Отрисовка Индикатора (Зона Б)
        draw_indicator_panel(screen, state)

        # 3. Отрисовка Поля (Зона В)
        draw_board(screen, state, TILE_SIZE, BOARD_START_X, BOARD_START_Y, font)

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        clock.tick(FPS)

    # 7. Завершение Pygame
    pygame.quit()
    sys.exit()

# Код ниже не будет выполнен из-за sys.exit()