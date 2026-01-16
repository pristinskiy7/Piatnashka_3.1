# game/constants.py


# --- ВЫСОТЫ ЗОН ---
INFO_PANEL_HEIGHT = 60
INDICATOR_HEIGHT = 60
BOARD_AREA_SIZE = 800 # Фиксированная область 600x600 для поля
BOARD_AREA_START_Y = INFO_PANEL_HEIGHT + INDICATOR_HEIGHT # = 120

FPS = 60
GAME_TITLE = "Пятнашка"

# Цвета (если не определены)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (240, 240, 240)
TILE_COLOR = (150, 150, 255)  # Цвет плитки (светло-голубой)
HIGHLIGHT_COLOR = (255, 200, 0) # Цвет для подсветки

# Отступы и поля
MARGIN = 10 # Отступ от краев окна
TILE_BORDER = 2 # Ширина рамки вокруг плитки