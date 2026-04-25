import os
import sys
from arcade import color

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Physics Constants
GRAVITY = 0.5
PLAYER_JUMP_VELOCITY = 5.5
PLAYER_MOVE_ACCEL = 0.7
PLAYER_FRICTION = 0.6

# Velocity Constants
CRAWL_VELOCITY = 0.5
NORMAL_VELOCITY = 1.5
SPRINT_VELOCITY = 2.5

# Max jumps
MAX_JUMPS = 2

# Stage config.
STAGE_CONFIG = {
    1:  {"color": color.DARK_BROWN},
    4:  {"color": color.DARK_OLIVE_GREEN, "speed": 5.5},
    8:  {"color": color.GRAY},
    10: {"speed": 1.5},
    11: {"color": color.PASTEL_BLUE},
    14: {"color": color.DESERT_SAND, "speed": 4},
    16: {"color": color.BABY_PINK},
    18: {"color": color.YELLOW_ORANGE},
    20: {"color": color.BLUEBERRY}
}