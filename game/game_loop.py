# game/game_loop.py

import pygame
import sys
from tkinter import messagebox
from game.state import get_state, init_game_state, set_state
import math
from game.logic import shuffle_board, make_move, is_tile_in_place
from settings.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
# ----------------------------------------------------


FPS = 60

# --- НОВЫЕ КОНСТАНТЫ (добавьте их в секцию КОНСТАНТЫ ОКНА И ДИЗАЙНА) ---
INDICATOR_PADDING_X = 10
INDICATOR_INNER_WIDTH = WINDOW_WIDTH - 2 * INDICATOR_PADDING_X # 1180
LOG_SCALE_POINTS = [0.01, 0.1, 1.0, 10.0] # Основные метки между 0 и N (площадью)
# -------------------------------------------------------------------------

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

# --- ДОБАВИТЬ НОВЫЙ ЦВЕТ ---
# Определите этот цвет в секции КОНСТАНТЫ ОКНА И ДИЗАЙНА в game/game_loop.py
TILE_COLOR_SOLVED = (100, 255, 100) # Ярко-зеленый цвет
TILE_COLOR = (150, 150, 255)        # Цвет плитки (оригинальный)
# ---------------------------

# ----------------------------------------------------
# ФУНКЦИИ ОТРЕСОВКИ
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
        f"Время: {state.get('time_elapsed', 0.0):.0f} сек.",  # <-- Ключ time_elapsed
        f"Ходов: {state.get('moves_count', 0)}",  # <-- Ключ moves_count
        f"K: {state.get('coeff_k', 0):.2f}"
    ]

    num_items = len(info_data)
    item_width = WINDOW_WIDTH // num_items

    is_playing = state.get('is_playing', False)

    # Подсветка кликабельной области Таймера (индекс 3)
    if not is_playing:
        # Индекс 3 соответствует элементу "Время"
        timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)
        # Визуальная подсказка, что можно кликнуть:
        pygame.draw.rect(screen, (255, 230, 150), timer_rect, 0)  # Желтоватый фон
        pygame.draw.rect(screen, (200, 100, 0), timer_rect, 3)  # Толстая оранжевая рамка

    # В ЦИКЛЕ РИСУЕТСЯ ТЕКСТ ПОВЕРХ ФОНА
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
    """Отрисовывает индикатор коэффициента K (Зона Б) по строго логарифмической шкале (база 10)."""
    rect = pygame.Rect(0, INFO_PANEL_HEIGHT, WINDOW_WIDTH, INDICATOR_HEIGHT)
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.line(screen, BLACK, (0, BOARD_AREA_START_Y), (WINDOW_WIDTH, BOARD_AREA_START_Y), 2)
    font = pygame.font.Font(None, 36)
    label_font = pygame.font.Font(None, 20)

    k_value = state.get('coeff_k', 0.0)
    board_w = state['board_w']
    board_h = state['board_h']
    board_n = board_w * board_h
    is_playing = state.get('is_playing', False)

    # --- 1. РАСЧЕТ ЛОГАРИФМИЧЕСКИХ КОНЦОВ ---

    K_MULTIPLIER = 1000
    K_MAX = board_n * K_MULTIPLIER

    # log_end: Логарифм максимальной метки (например, log10(100000) = 5.0)
    log_end = math.log10(K_MAX)

    # LOG_START: Начало шкалы (на 5 порядков меньше). Range = 5.0.
    LOG_START = log_end - 5.0
    log_range = 5.0

    # K_MIN_MARK: Минимальная метка, которую мы отображаем (например, 1.0 для 10x10)
    K_MIN_MARK = 10 ** LOG_START

    # Нормализация K
    if k_value <= K_MIN_MARK:  # Теперь все, что меньше минимальной метки, считается 0% шкалы
        log_k = LOG_START
        normalized_k = 0.0
    else:
        log_k = math.log10(k_value)
        normalized_k = (log_k - LOG_START) / log_range

    normalized_k = min(1.0, max(0.0, normalized_k))
    indicator_width = normalized_k * INDICATOR_INNER_WIDTH

    # Определяем цвет
    color_ratio = normalized_k
    red = int(255 * (1 - color_ratio))
    green = int(255 * color_ratio)
    color = (red, green, 0)

    # --- 2. Отрисовка Шкалы (6 Мето к) ---
    scale_y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT - 10

    log_marks = []

    # Генерируем 6 меток: от K_MAX / 10^5 до K_MAX / 10^0
    for i in range(6):
        # K_MAX / 10^(5 - i)
        mark_value = K_MAX / (10 ** (5 - i))

        # Для удобства чтения округляем, если число целое
        if mark_value >= 1:
            log_marks.append(round(mark_value))
        else:
            log_marks.append(mark_value)

    # Рисуем метки
    for val in log_marks:

        if val == K_MAX:
            normalized_pos = 1.0
        # Рассчитываем позицию для всех меток, используя LOG_START
        else:
            if val < K_MIN_MARK:
                # Позиция минимальной метки (самый левый край)
                log_val = LOG_START
            else:
                log_val = math.log10(val)

            normalized_pos = (log_val - LOG_START) / log_range

        normalized_pos = min(1.0, max(0.0, normalized_pos))
        pos_x = INDICATOR_PADDING_X + normalized_pos * INDICATOR_INNER_WIDTH

        pygame.draw.line(screen, BLACK, (pos_x, scale_y - 8), (pos_x, scale_y), 1)

        # Форматирование
        text_format = ".2f" if val < 1.0 else "g"
        text_surf = label_font.render(f"{val:{text_format}}", True, BLACK)
        screen.blit(text_surf, (pos_x - text_surf.get_width() // 2, scale_y + 2))

    # --- 3. Отрисовка Полосы ---
    k_rect = pygame.Rect(INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, indicator_width, INDICATOR_HEIGHT - 20)

    if is_playing:
        pygame.draw.rect(screen, color, k_rect, 0)

    pygame.draw.rect(screen, BLACK, k_rect, 1)

    # --- 4. Отрисовка Текущего Значения K ---
    current_k_text = f"K: {k_value:.4f} (Max: {K_MAX:g})"  # ИСПРАВЛЕНО
    text_surf = font.render(current_k_text, True, BLACK)

    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, INFO_PANEL_HEIGHT + INDICATOR_HEIGHT // 2))
    screen.blit(text_surf, text_rect)
    # --- 3. Отрисовка Полосы ---
    k_rect = pygame.Rect(INDICATOR_PADDING_X, INFO_PANEL_HEIGHT + 10, indicator_width, INDICATOR_HEIGHT - 20)

    if is_playing:
        pygame.draw.rect(screen, color, k_rect, 0)

    pygame.draw.rect(screen, BLACK, k_rect, 1)

    # --- 4. Отрисовка Текущего Значения K ---
    current_k_text = f"K: {k_value:.4f} (Max: {K_MAX:g})"  # ИСПРАВЛЕНО
    text_surf = font.render(current_k_text, True, BLACK)

    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, INFO_PANEL_HEIGHT + INDICATOR_HEIGHT // 2))
    screen.blit(text_surf, text_rect)


def draw_board(screen, state, TILE_SIZE, start_x, start_y, font):
    """Отрисовывает игровое поле и плитки (Зона В)."""

    board = state['tiles']
    board_w = state['board_w']
    board_h = state['board_h']

    # Рисуем общую рамку поля
    board_rect = pygame.Rect(start_x - TILE_BORDER, start_y - TILE_BORDER,
                             (TILE_SIZE * board_w) + TILE_BORDER * 2,
                             (TILE_SIZE * board_h) + TILE_BORDER * 2)
    pygame.draw.rect(screen, BLACK, board_rect, TILE_BORDER)

    # --- ИМПОРТ is_tile_in_place ДОЛЖЕН БЫТЬ В НАЧАЛЕ ФАЙЛА ---
    # Мы используем его здесь, предполагая, что импорт работает корректно

    for row in range(board_h):
        for col in range(board_w):
            tile_value = board[row][col]

            x = start_x + col * TILE_SIZE
            y = start_y + row * TILE_SIZE

            if tile_value != 0:

                # ------------------------------------------------------------------
                # НОВАЯ ЛОГИКА: ОПРЕДЕЛЕНИЕ ЦВЕТА ПЛИТКИ
                # ------------------------------------------------------------------
                if is_tile_in_place(tile_value, row, col, board_w, board_h):
                    current_tile_color = TILE_COLOR_SOLVED  # Зеленый
                else:
                    current_tile_color = TILE_COLOR  # Оригинальный синий/фиолетовый

                # 1. Рисуем фоновую плитку (ТОЛЬКО ОДИН РАЗ, ИСПОЛЬЗУЯ current_tile_color)
                pygame.draw.rect(screen, current_tile_color, (x, y, TILE_SIZE, TILE_SIZE))

                # 2. Рисуем рамку
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), TILE_BORDER)

                # 3. Рисуем число
                text_size = TILE_SIZE // 2
                tile_font = pygame.font.Font(None, max(36, text_size))

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

    # 2. Скрываем окно меню Tkinter
    menu_root.withdraw()
    print(f"ЛОГ: Запуск Pygame для игрока {player_name} на поле {board_w}x{board_h}...")

    # --- КРИТИЧЕСКИЙ БЛОК ИНИЦИАЛИЗАЦИИ PYGAME ---
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

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
    # БЛОК: РАСЧЕТ РАЗМЕРА ИГРОВОГО ПОЛЯ
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

    # Инициализация времени для delta_time
    last_time = pygame.time.get_ticks()

    # ----------------------------------------------------
    # ГЛАВНЫЙ ЦИКЛ ИГРЫ
    # ----------------------------------------------------
    running = True
    while running:

        # ------------------------------------------------------------------
        # Расчет Delta Time и Обновление Таймера
        # ------------------------------------------------------------------
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # Время в секундах
        last_time = current_time

        state = get_state()
        is_playing = state.get('is_playing', False)

        # Обновление таймера, если игра активна
        if is_playing:
            new_time = state.get('time_elapsed', 0.0) + delta_time
            set_state('time_elapsed', new_time)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                    # --- ЛОГИКА: ОБРАБОТКА КЛИКА МЫШИ ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                # --- ДИАГНОСТИКА: КЛИК ---
                print(f"КЛИК: Обнаружен на ({mouse_x}, {mouse_y}). is_playing: {is_playing}")

                # 1. Клик по Таймеру (Запуск игры)
                if not is_playing:

                    num_items = 6
                    item_width = WINDOW_WIDTH // num_items
                    timer_rect = pygame.Rect(3 * item_width, 0, item_width, INFO_PANEL_HEIGHT)

                    # --- ДИАГНОСТИКА: RECT ---
                    print(f"ТАЙМЕР RECT: {timer_rect}. COLLIDEPOINT: {timer_rect.collidepoint(mouse_x, mouse_y)}")

                    if timer_rect.collidepoint(mouse_x, mouse_y):
                        shuffle_board()  # Запускает перемешивание и устанавливает is_playing=True
                        last_time = pygame.time.get_ticks()  # Сброс, чтобы время не скакнуло
                        print("ЛОГ КЛИКА: Клик по Таймеру успешно обработан, вызов shuffle.")

                # 2. Клик по игровому полю (ход)
                elif is_playing:

                    # Проверка, что клик находится в области доски (для эффективности)
                    if mouse_y >= BOARD_START_Y and mouse_x >= BOARD_START_X:

                        # Расчет координат ячейки
                        offset_x = mouse_x - BOARD_START_X
                        offset_y = mouse_y - BOARD_START_Y

                        col = offset_x // TILE_SIZE
                        row = offset_y // TILE_SIZE

                        # Проверка, что координаты в пределах доски
                        if 0 <= row < board_h and 0 <= col < board_w:
                            make_move(row, col)  # Вызываем функцию хода
                            print(f"ЛОГ ХОДА: Клик по плитке в ({row}, {col}).")

        # ----------------------------------------------------
        # 6. Отрисовка
        # ----------------------------------------------------

        screen.fill(BACKGROUND_COLOR)

        draw_info_panel(screen, state, font)
        draw_indicator_panel(screen, state)

        # Обновляем board_h/board_w, так как они используются в логике клика выше
        board_h = state['board_h']
        board_w = state['board_w']

        draw_board(screen, state, TILE_SIZE, BOARD_START_X, BOARD_START_Y, font)

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        clock.tick(FPS)

    # 7. Завершение Pygame
    pygame.quit()
    sys.exit()