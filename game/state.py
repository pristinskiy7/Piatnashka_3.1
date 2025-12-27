# game/state.py
import pygame
import datetime
from game.logic import new_game, is_finished
from ui.elements import UI_HEIGHT_MENU
from ui import events as ui_events
from players.manager import save_result   # функция записи истории

EMPTY_VALUE = 0  # единый формат пустой клетки


class GameState:
    def __init__(self):
        # --- UI состояние ---
        self.selected_input = None
        self.dropdown_open = False
        self.scroll_offset = 0

        # --- Команда ---
        self.team_name = ""   # название команды на этом компьютере

        # --- Игроки ---
        self.active_name = ""   # активный игрок
        self.adding_player = False
        self.input_player_name = ""

        # --- Настройки поля ---
        self.w_mode = None
        self.h_mode = None
        self.input_width = ""
        self.input_height = ""

        # --- Игровой процесс ---
        self.game_started = False
        self.start_time = 0

        # --- Размеры плиток (инициализируются позже при resize_board) ---
        self.tile_w = 0
        self.tile_h = 0

    def resize_board(self, w, h):
        # пример: пересчёт размеров плиток
        self.tile_w = 600 // w
        self.tile_h = 600 // h

    def _make_solved_board(self, w, h):
        board = []
        val = 1
        for y in range(h):
            row = []
            for x in range(w):
                row.append(val)
                val += 1
            board.append(row)
        board[h - 1][w - 1] = EMPTY_VALUE
        return board

    def find_empty(self):
        for y in range(self.h):
            for x in range(self.w):
                if self.board[y][x] == EMPTY_VALUE:
                    return (x, y)
        return None

    def try_move(self, tile_x, tile_y):
        # проверка на выход за границы
        if not (0 <= tile_x < self.w and 0 <= tile_y < self.h):
            return False

        ep = self.find_empty()
        if ep is None:
            return False
        empty_x, empty_y = ep

        if tile_y == empty_y:
            row = self.board[empty_y]

            if tile_x < empty_x:
                segment = row[tile_x:empty_x]
                row[tile_x + 1:empty_x + 1] = segment
                row[tile_x] = EMPTY_VALUE
                self.empty_pos = (tile_x, tile_y)

            elif tile_x > empty_x:
                segment = row[empty_x + 1:tile_x + 1]
                row[empty_x:tile_x] = segment
                row[tile_x] = EMPTY_VALUE
                self.empty_pos = (tile_x, tile_y)

            else:
                return False

        elif tile_x == empty_x:
            col = [self.board[y][empty_x] for y in range(self.h)]

            if tile_y < empty_y:
                segment = col[tile_y:empty_y]
                for y in range(tile_y + 1, empty_y + 1):
                    self.board[y][empty_x] = segment[y - (tile_y + 1)]
                self.board[tile_y][empty_x] = EMPTY_VALUE
                self.empty_pos = (tile_x, tile_y)

            elif tile_y > empty_y:
                segment = col[empty_y + 1:tile_y + 1]
                for y in range(empty_y, tile_y):
                    self.board[y][empty_x] = segment[y - empty_y]
                self.board[tile_y][empty_x] = EMPTY_VALUE
                self.empty_pos = (tile_x, tile_y)

            else:
                return False
        else:
            return False

        # один ход
        self.moves += 1

        # проверка на победу
        if is_finished(self.board):
            print(">>> Победа зафиксирована!")  # отладка
            self.finished = True
            self.finish_time = (pygame.time.get_ticks() - self.start_time) // 1000
            if ui_events.active_name:
                print(f">>> Сохраняем результат игрока {ui_events.active_name}")  # отладка
                save_result(
                    ui_events.active_name,
                    self.w,
                    self.h,
                    self.moves,
                    self.finish_time,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

        return True

    def elapsed_time(self):
        if self.finished and self.finish_time is not None:
            print(f">>> Таймер остановлен на {self.finish_time} сек")  # отладка
            return self.finish_time
        return (pygame.time.get_ticks() - self.start_time) // 1000

    def check_finished(self):
        if not self.finished and is_finished(self.board):
            print(">>> Победа зафиксирована через check_finished!")  # отладка
            self.finished = True
            self.finish_time = (pygame.time.get_ticks() - self.start_time) // 1000
            if ui_events.active_name:
                print(f">>> Сохраняем результат игрока {ui_events.active_name}")  # отладка
                save_result(
                    ui_events.active_name,
                    self.w,
                    self.h,
                    self.moves,
                    self.finish_time,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

    def resize_board(self, w, h):
        """Пересоздать игровое поле с новыми размерами"""
        self.w = w
        self.h = h
        self.board = new_game(w, h)
        if self.board is None:
            print(">>> new_game вернул None при resize. Создаём собранную раскладку.")
            self.board = self._make_solved_board(w, h)

        self.moves = 0
        self.start_time = pygame.time.get_ticks()
        self.finished = False
        self.finish_time = None   # ← добавлено
        self.tile_w = UI_HEIGHT_MENU // w
        self.tile_h = UI_HEIGHT_MENU // h
        self.empty_pos = self.find_empty()
        if self.empty_pos is None:
            self.board[self.h - 1][self.w - 1] = EMPTY_VALUE
            self.empty_pos = (self.w - 1, self.h - 1)