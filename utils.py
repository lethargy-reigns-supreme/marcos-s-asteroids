from pygame.image import load
from pygame.math import Vector2

import random


def load_sprite(folder, name, file_type, with_alpha=True):

    path = f"graphics/{folder}/{name}.{file_type}"
    loaded_sprite = load(path)

    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()


def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % w, y % h)


def get_random_position(surface):
    return Vector2(
        random.randrange(surface.get_width()),
        random.randrange(surface.get_height())
    )


def get_random_vel(min_vel, max_vel):
    speed = random.randint(min_vel, max_vel)
    angle = random.randrange(0, 360)

    return Vector2(speed, 0).rotate(angle)
