# game/board_draw.py

import pygame
from ui.elements import font, UI_WIDTH_MENU, MENU_ELEMENTS, DROPDOWN_ELEMENTS

# --- функция отрисовки окна MENU ---
def draw_menu(screen, state):
    screen.fill((220, 220, 220))

    ## Заголовок
    title_text = font.render("Меню", True, (0, 0, 0))
    screen.blit(title_text, (UI_WIDTH_MENU // 2 - title_text.get_width() // 2, 20))

    # Многострочная инструкция
    instructions = [
        "Здесь нужно зарегистрироваться, все игроки на одном компьютере обьединяются",
        "в команду. Ввести название команды выбрать или ввести имя нового игрока,",
        "(в одной команде не должно быть одинаковых имён игроков)",
        "а также задать ширину и высоту игрового поля, либо оставить случайные значения.",
        "После этого нажмите кнопку 'Старт'."
    ]

    y_offset = 50  # начальная высота для первой строки
    for line in instructions:
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += text_surface.get_height() + 1  # отступ между строками

    rect = MENU_ELEMENTS["team_name"]["rect"]
    color = (150, 200, 250) if state.selected_input == "team_name" else (180, 180, 180)
    pygame.draw.rect(screen, color, rect, border_radius=6)

    # если команда уже сохранена → показываем её, иначе стандартную надпись
    label = state.team_name if state.team_name else MENU_ELEMENTS["team_name"]["label"]
    text = font.render(label, True, (0, 0, 0))
    text_rect = text.get_rect(center=rect.center)
    screen.blit(text, text_rect)

    # Отрисовка всех элементов меню, кроме "team_name"
    for key, element in MENU_ELEMENTS.items():
        if key == "team_name":
            continue  # поле "Команда" уже отрисовано отдельно

        rect = element["rect"]
        label = element["label"]

        pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=6)
        text = font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # --- Отрисовка dropdown-меню (если нужно) ---
    for key, element in DROPDOWN_ELEMENTS.items():
        rect = element["rect"]
        pygame.draw.rect(screen, (200, 200, 220), rect, border_radius=6)
        # можно добавить текст или список опций
