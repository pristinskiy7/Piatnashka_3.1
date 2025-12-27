# main.py

import pygame
from game.state import GameState
from game.board_draw import  draw_menu
import ui.events as ui_events
from  ui.elements import UI_WIDTH_MENU, UI_HEIGHT_MENU
from settings.manager import load_settings


def main():
    pygame.init()
    screen = pygame.display.set_mode((UI_WIDTH_MENU, UI_HEIGHT_MENU))
    pygame.display.set_caption("Пятнашка 3.1")

    state = GameState()
    state.start_time = None

    # Загружаем сохранённые настройки
    settings = load_settings()
    state.team_name = settings.get("team_name", "")
    state.team_confirmed = bool(state.team_name)  # ← новый флаг

    clock = pygame.time.Clock()
    current_scene = "menu"
    running = True


    while running:
        if current_scene == "menu":
            # обработка событий меню
            running = ui_events.handle_events(state)
            # отрисовка меню
            draw_menu(screen, state)
            # переход к игре
            if getattr(state, "game_started", False):
                current_scene = "game"

        elif current_scene == "game":
            running = ui_events.handle_events(state)
            elapsed_sec = (pygame.time.get_ticks() - state.start_time) // 1000 if state.start_time else 0
            draw_board(screen, state.board, state.moves, elapsed_sec, state)
            if state.finished:
                current_scene = "results"

        elif current_scene == "results":
            draw_results(screen, state)
            # здесь можно добавить кнопку "Новая игра" или "Выход"

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()