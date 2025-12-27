# ui/inputs.py
import pygame
from ui.elements import (
    WIDTH_RECT,
    HEIGHT_RECT,
    START_RECT,
    PLAYER_NAME_RECT,
    DROPDOWN_RECT,
    WIDTH_DROPDOWN_RECT,
    HEIGHT_DROPDOWN_RECT,
    font,
)
from players.manager import load_players
from ui import events as ui_events


def draw_inputs(screen, dropdown_open, scroll_offset):
    # --- Поле имени игрока ---
    if ui_events.adding_player:
        pygame.draw.rect(screen, (250, 250, 180), PLAYER_NAME_RECT, border_radius=6)
        text = ui_events.input_player_name or "Новый игрок..."
        name_text = font.render(text, True, (0, 0, 0))
    else:
        pygame.draw.rect(screen, (180, 180, 180), PLAYER_NAME_RECT, border_radius=6)
        current_name = ui_events.active_name or "Имя игрока"
        color = (0, 0, 0) if ui_events.active_name else (80, 80, 80)
        name_text = font.render(current_name, True, color)

    screen.blit(name_text, name_text.get_rect(center=PLAYER_NAME_RECT.center))

    # --- Поле ширины ---
    pygame.draw.rect(screen, (200, 200, 200), WIDTH_RECT, border_radius=6)
    if ui_events.w_mode == "random":
        w_text = font.render("WR", True, (0, 0, 0))
    elif ui_events.w_mode == "set" and ui_events.input_width:
        w_text = font.render(f"W {ui_events.input_width}", True, (0, 0, 0))
    else:
        w_text = font.render("W", True, (0, 0, 0))
    screen.blit(w_text, w_text.get_rect(center=WIDTH_RECT.center))

    # --- Поле высоты ---
    pygame.draw.rect(screen, (200, 200, 200), HEIGHT_RECT, border_radius=6)
    if ui_events.h_mode == "random":
        h_text = font.render("HR", True, (0, 0, 0))
    elif ui_events.h_mode == "set" and ui_events.input_height:
        h_text = font.render(f"H {ui_events.input_height}", True, (0, 0, 0))
    else:
        h_text = font.render("H", True, (0, 0, 0))
    screen.blit(h_text, h_text.get_rect(center=HEIGHT_RECT.center))



    # --- Кнопка "Старт" ---
    pygame.draw.rect(screen, (180, 180, 250), START_RECT, border_radius=6)
    start_text = font.render("Старт", True, (0, 0, 0))
    screen.blit(start_text, start_text.get_rect(center=START_RECT.center))

    # --- Dropdown ---
    if dropdown_open:
        if ui_events.selected_input == "player_dropdown":
            draw_player_dropdown(screen, DROPDOWN_RECT, scroll_offset)
        elif ui_events.selected_input == "width_mode":
            draw_size_dropdown(screen, WIDTH_DROPDOWN_RECT, scroll_offset, "W")
        elif ui_events.selected_input == "height_mode":
            draw_size_dropdown(screen, HEIGHT_DROPDOWN_RECT, scroll_offset, "H")


def draw_player_dropdown(screen, rect, scroll_offset):
    players = load_players()
    names = [p["name"] for p in players] + ["Новый игрок"]

    pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)

    item_height = 40
    padding = 5
    step = item_height + padding

    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    y = -scroll_offset
    for name in names:
        item_rect = pygame.Rect(5, y, rect.width - 10, item_height)
        if item_rect.bottom >= 0 and item_rect.top <= rect.height:
            pygame.draw.rect(surface, (255, 255, 255), item_rect, border_radius=4)
            text = font.render(name, True, (0, 0, 0))
            surface.blit(text, text.get_rect(midleft=(item_rect.x + 10, item_rect.centery)))
        y += step

    screen.blit(surface, (rect.x, rect.y))


def draw_size_dropdown(screen, rect, scroll_offset, axis):
    options = ["Случайная", "Задать"]
    pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)

    item_height = 40
    padding = 5
    step = item_height + padding

    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    y = -scroll_offset
    for opt in options:
        item_rect = pygame.Rect(5, y, rect.width - 10, item_height)
        if item_rect.bottom >= 0 and item_rect.top <= rect.height:
            pygame.draw.rect(surface, (255, 255, 255), item_rect, border_radius=4)
            text = font.render(opt, True, (0, 0, 0))
            surface.blit(text, text.get_rect(midleft=(item_rect.x + 10, item_rect.centery)))
        y += step

    screen.blit(surface, (rect.x, rect.y))