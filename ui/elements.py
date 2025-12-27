# ui/elements.py

import pygame

pygame.font.init()

UI_METR = 1000  # базовая метрика для UI
UI_WIDTH_MENU = UI_METR * 0.8
UI_HEIGHT_MENU = UI_METR * 0.6

WINDOW_WIDTH_MENU = UI_WIDTH_MENU
WINDOW_HEIGHT_MENU = UI_HEIGHT_MENU

font = pygame.font.SysFont("arial", 24)

# словарь элементов меню
MENU_ELEMENTS = {
    "team_name": {
        "rect": pygame.Rect(UI_METR*0.02, 200, UI_METR*0.2, 40),
        "label": "Kомандa"
    },
    "player_name": {
        "rect": pygame.Rect(UI_METR*0.24, 200, UI_METR*0.2, 40),
        "label": "Имя игрока"
    },
    "width": {
        "rect": pygame.Rect(UI_METR*0.46, 200, UI_METR*0.13, 40),
        "label": "Ширина поля"
    },
    "height": {
        "rect": pygame.Rect(UI_METR*0.61, 200, UI_METR*0.13, 40),
        "label": "Высота поля"
    },
    "start": {
        "rect": pygame.Rect(20, 300, UI_METR*0.2, 40),
        "label": "Старт"
    }
}

# словарь dropdown-меню
DROPDOWN_ELEMENTS = {
    "player_name": {
        "rect": pygame.Rect(MENU_ELEMENTS["player_name"]["rect"].x,
                            MENU_ELEMENTS["player_name"]["rect"].bottom + 10,
                            MENU_ELEMENTS["player_name"]["rect"].width,
                            400)
    },
    "width": {
        "rect": pygame.Rect(MENU_ELEMENTS["width"]["rect"].x,
                            MENU_ELEMENTS["width"]["rect"].bottom + 5,
                            MENU_ELEMENTS["width"]["rect"].width,
                            80)
    },
    "height": {
        "rect": pygame.Rect(MENU_ELEMENTS["height"]["rect"].x,
                            MENU_ELEMENTS["height"]["rect"].bottom + 5,
                            MENU_ELEMENTS["height"]["rect"].width,
                            80)
    }
}
team_name = ""   # глобальная переменная для названия команды
