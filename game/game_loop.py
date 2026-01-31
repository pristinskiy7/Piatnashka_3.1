# game/game_loop.py


import pygame

from game.logic import (
    shuffle_board, make_move, is_tile_in_place,
    calculate_current_xp, is_solved, get_rank_info
)
from game.state import get_state, init_game_state, set_state
from settings.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from players.manager import save_result

# --- КОНСТАНТЫ ---
FPS = 60
INFO_PANEL_HEIGHT = 80
INDICATOR_HEIGHT = 60
BOARD_AREA_SIZE = 600
BOARD_AREA_START_Y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT
# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (220, 220, 220)
BOARD_BG_COLOR = (80, 80, 80)
TILE_COLOR = (150, 150, 255)
TILE_COLOR_SOLVED = (100, 255, 100)
GOLD = (255, 215, 0)


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ОТРИСОВКИ ---

def draw_info_panel(screen, state, font):
    pygame.draw.rect(screen, (180, 180, 240), (0, 0, WINDOW_WIDTH, INFO_PANEL_HEIGHT))
    rank = state.get('rank_title', 'Новичок')
    player = state.get('player_name', 'Player')

    txt = font.render(f"[{rank}] {player}", True, BLACK)
    screen.blit(txt, (20, 10))

    stats = f"Время: {int(state.get('time_elapsed', 0))}с | Ходы: {state.get('moves_count', 0)}"
    stats_surf = font.render(stats, True, (50, 50, 50))
    screen.blit(stats_surf, (20, 45))

    is_playing = state.get('is_playing', False)
    btn_rect = pygame.Rect(WINDOW_WIDTH - 160, 10, 140, 60)
    pygame.draw.rect(screen, (255, 230, 150) if not is_playing else (150, 255, 150), btn_rect, border_radius=5)
    pygame.draw.rect(screen, BLACK, btn_rect, 2, border_radius=5)
    btn_txt = font.render("СТАРТ" if not is_playing else "ЗАНОВО", True, BLACK)
    screen.blit(btn_txt, btn_txt.get_rect(center=btn_rect.center))


def draw_indicator_panel(screen, state):
    rect = pygame.Rect(0, INFO_PANEL_HEIGHT, WINDOW_WIDTH, INDICATOR_HEIGHT)
    pygame.draw.rect(screen, (235, 235, 235), rect)
    font_small = pygame.font.Font(None, 28)

    predicted_xp = state.get('coeff_k', 0)
    xp_text = f"Прогноз награды: {int(predicted_xp)} XP"
    xp_surf = font_small.render(xp_text, True, BLACK)
    screen.blit(xp_surf, (WINDOW_WIDTH // 2 - xp_surf.get_width() // 2, INFO_PANEL_HEIGHT + 10))

    md_initial = max(state.get('md_initial', 1), 1)
    moves = max(state.get('moves_count', 0), 1)
    accuracy = min(1.0, md_initial / moves)

    padding_x = 40
    bar_w = WINDOW_WIDTH - (padding_x * 2)
    bg_bar = pygame.Rect(padding_x, INFO_PANEL_HEIGHT + 38, bar_w, 10)
    pygame.draw.rect(screen, (200, 200, 200), bg_bar, border_radius=5)

    if state.get('is_playing', False):
        color = (100, 150, 255) if accuracy < 0.8 else GOLD
        fill_w = int(bar_w * accuracy)
        pygame.draw.rect(screen, color, (padding_x, INFO_PANEL_HEIGHT + 38, fill_w, 10), border_radius=5)


def draw_victory_screen(screen, state, font):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    card = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 150, 400, 300)
    pygame.draw.rect(screen, WHITE, card, border_radius=15)
    pygame.draw.rect(screen, GOLD, card, 5, border_radius=15)

    title = pygame.font.Font(None, 50).render("ГОТОВО!", True, (0, 120, 0))
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, card.top + 50)))

    # Используем текущий total_xp из состояния для прогресс-бара
    level, xp_in, xp_req, progress, rank_name = get_rank_info(state.get('total_xp', 0))
    bar_rect = pygame.Rect(card.left + 50, card.top + 150, 300, 30)
    pygame.draw.rect(screen, (220, 220, 220), bar_rect, border_radius=10)
    pygame.draw.rect(screen, (50, 150, 255), (bar_rect.x, bar_rect.y, int(bar_rect.w * progress), bar_rect.h),
                     border_radius=10)

    lvl_txt = font.render(f"Уровень {level}: {rank_name}", True, BLACK)
    screen.blit(lvl_txt, (bar_rect.left, bar_rect.top - 35))


# --- ОСНОВНОЙ ЦИКЛ ---

def start_game_loop(menu_root, player_name, board_w, board_h):
    # 1. Инициализация состояния
    init_game_state(player_name, board_w, board_h)

    # 2. АВТО-СТАРТ: Сразу генерируем раскладку
    shuffle_board()

    menu_root.withdraw()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    TILE_SIZE = min(BOARD_AREA_SIZE // board_w, BOARD_AREA_SIZE // board_h)
    OFF_X = (WINDOW_WIDTH - (TILE_SIZE * board_w)) // 2
    OFF_Y = BOARD_AREA_START_Y + (BOARD_AREA_SIZE - (TILE_SIZE * board_h)) // 2

    running = True
    already_saved = False  # Контроль однократной записи

    while running:
        dt = clock.tick(FPS) / 1000.0
        state = get_state()
        is_playing = state.get('is_playing', False)

        if is_playing:
            set_state('time_elapsed', state.get('time_elapsed', 0.0) + dt)
            set_state('coeff_k', calculate_current_xp())
            already_saved = False  # Сбрасываем, когда началась новая игра

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                btn_rect = pygame.Rect(WINDOW_WIDTH - 160, 10, 140, 60)
                if btn_rect.collidepoint(mx, my):
                    shuffle_board()
                elif is_playing:
                    c = (mx - OFF_X) // TILE_SIZE
                    r = (my - OFF_Y) // TILE_SIZE
                    if 0 <= r < board_h and 0 <= c < board_w:
                        make_move(r, c)

        # --- ЛОГИКА СОХРАНЕНИЯ ПОБЕДЫ ---
        if not is_playing and state.get('moves_count', 0) > 0:
            if is_solved(state) and not already_saved:
                # Фиксируем данные
                f_moves = state.get('moves_count', 0)
                f_time = int(state.get('time_elapsed', 0))
                f_xp = int(state.get('coeff_k', 0))

                # Сохраняем в JSON
                save_result(f_moves, f_time, f_xp, (board_w, board_h))

                # Обновляем локальный state для красоты полоски уровня
                new_total = state.get('total_xp', 0) + f_xp
                set_state('total_xp', new_total)

                already_saved = True  # Запираем замок

        # --- ОТРИСОВКА ---
        screen.fill(BACKGROUND_COLOR)

        board_full_w, board_full_h = board_w * TILE_SIZE, board_h * TILE_SIZE
        board_rect = pygame.Rect(OFF_X, OFF_Y, board_full_w, board_full_h)
        pygame.draw.rect(screen, BOARD_BG_COLOR, board_rect)
        pygame.draw.rect(screen, BLACK, board_rect, 4)

        tiles = state.get('tiles', [])
        if tiles:
            for r in range(board_h):
                for c in range(board_w):
                    val = tiles[r][c]
                    if val != 0:
                        correct = is_tile_in_place(val, r, c, board_w, board_h)
                        color = TILE_COLOR_SOLVED if correct else TILE_COLOR
                        rect = (OFF_X + c * TILE_SIZE, OFF_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)
                        t_surf = font.render(str(val), True, BLACK)
                        screen.blit(t_surf,
                                    t_surf.get_rect(center=(rect[0] + TILE_SIZE // 2, rect[1] + TILE_SIZE // 2)))

        draw_info_panel(screen, state, font)
        draw_indicator_panel(screen, state)

        if not is_playing and state.get('moves_count', 0) > 0:
            if is_solved(state):
                draw_victory_screen(screen, state, font)

        pygame.display.flip()

    pygame.quit()
    menu_root.deiconify()