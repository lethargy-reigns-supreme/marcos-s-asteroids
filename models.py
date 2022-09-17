import pygame
from utils import *
from random import randint
from math import atan2, cos, sin

UP = pygame.math.Vector2(0, 1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = pygame.math.Vector2(position)
        self.sprite = sprite
        self.mask = pygame.mask.from_surface(sprite)
        self.radius = self.sprite.get_width() / 2
        self.velocity = pygame.math.Vector2(velocity)

    def other_draw(self, surface):
        blit_position = self.position - pygame.math.Vector2(self.radius)
        surface.blit(self.mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255)), blit_position)

    def draw(self, surface):
        blit_position = self.position - pygame.math.Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        offset = (other_obj.position[0] - self.position[0], other_obj.position[-1] - self.position[-1])
        return self.mask.overlap(other_obj.mask, offset)


class Spaceship(GameObject):
    ACCELERATION = 0.25
    MANEUVERABILITY = 5
    BULLET_VEL = 7

    def __init__(self, position, create_bullet_callback):
        super().__init__(position, load_sprite('player', 'spaceship-cookie', 'png'), pygame.math.Vector2(0))

        self.create_bullet_callback = create_bullet_callback

        self.direction = pygame.math.Vector2(UP)

    def shoot(self):
        bullet_vel = self.direction * self.BULLET_VEL + self.velocity
        bullet = Bullet(self.position, bullet_vel)
        self.create_bullet_callback(bullet)

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = pygame.transform.rotate(self.sprite, angle)
        rotated_surface_size = pygame.math.Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size*0.5
        surface.blit(rotated_surface, blit_position)

    def other_draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = pygame.transform.rotate(self.sprite, angle)
        self.mask = pygame.mask.from_surface(rotated_surface)
        rotated_surface_size = pygame.math.Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(self.mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255)), blit_position)


class Asteroid(GameObject):

    def __init__(self, position, create_asteroid_callback, size=3):
        self.create_asteroid_callback = create_asteroid_callback

        num = randint(1, 3)

        self.size = size
        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25
        }

        scale = size_to_scale[size]

        image = ''

        if num == 1:
            image = 'cookie-comet1'
        elif num == 2:
            image = 'cookie-comet2'
        if num == 3:
            image = 'cookie-comet3'

        sprite = pygame.transform.rotozoom(load_sprite('cookie-comets', image, 'png'), 0, scale)

        super().__init__(position, sprite, get_random_vel(1, 3))

    def split(self):
        if self.size > 1:
            for i in range(2):
                asteroid = Asteroid(self.position, self.create_asteroid_callback, self.size - 1)
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    MANEUVERABILITY = 10

    def __init__(self, position, velocity):
        super().__init__(position, load_sprite('player', 'choco-bullet', 'png'), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity

    def draw(self, surface):
        rotated_sprite = pygame.transform.rotate(self.sprite, self.MANEUVERABILITY)
        blit_position = self.position - pygame.math.Vector2(self.radius)

        surface.blit(rotated_sprite, blit_position)


class UFO(GameObject):
    BULLET_VEL = 4

    def __init__(self, position, velocity, create_bullet_callback):
        super().__init__(position, load_sprite('player', 'spaceship-cookie', 'png'), velocity)

        self.shoot_direction = pygame.math.Vector2(UP)

        self.create_bullet_callback = create_bullet_callback

    def find_dir(self, spaceship):
        radians = atan2(spaceship.position.y - self.position.y, spaceship.position.x - self.position.x)
        self.shoot_direction.x = cos(radians) * self.BULLET_VEL
        self.shoot_direction.y = sin(radians) * self.BULLET_VEL

    def shoot(self, spaceship):
        self.find_dir(spaceship)
        bullet_vel = self.shoot_direction + self.velocity
        bullet = Bullet(pygame.math.Vector2(self.position), bullet_vel)
        self.create_bullet_callback(bullet)

    def collides_with(self, other_obj):
        offset = (other_obj.position[0] - self.position.x, other_obj.position[-1] - self.position.y)
        return self.mask.overlap(other_obj.mask, offset)
