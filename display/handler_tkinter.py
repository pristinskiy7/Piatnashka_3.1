# ui/handler_tkinter.py

# Переменная для хранения следующей сцены, которую вернет Tkinter
NEXT_SCENE = 'exit'


def set_next_scene(scene_name):
    """Устанавливает имя следующей сцены, куда должен перейти main.py."""
    global NEXT_SCENE
    NEXT_SCENE = scene_name


def get_next_scene():
    """Возвращает установленное имя следующей сцены."""
    return NEXT_SCENE