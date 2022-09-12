import pygame
from utils import load_sprite, get_random_position
from models import Spaceship, Asteroid


#   main game class
class CookieComet:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):

        #   pygame initialization
        self.game_active = False
        self.show_mask = False
        self._init_pygame()

        #   creating screen
        self.W, self.H = 1370, 710
        self.screen = pygame.display.set_mode((self.W, self.H))

        #   image loading
        self.cookie_icon = pygame.image.load('graphics/other/cookie-comet-icon.ico')
        pygame.display.set_icon(self.cookie_icon)
        self.background = load_sprite('other', 'milky-way-2695569__480', 'jpg', False)

        #   game objects
        self.bullets = []
        self.spaceship = Spaceship((self.W/2, self.H/2), self.bullets.append)
        self.asteroids = []
        self.big_asteroids = []

        for i in range(3):
            while True:
                position = get_random_position(self.screen)
                if position.distance_to(self.spaceship.position) > self.MIN_ASTEROID_DISTANCE:
                    break
            
            self.asteroids.append(Asteroid(position, self.asteroids.append))

        for asteroid in self.asteroids:
            if asteroid.size == 3:
                self.big_asteroids.append(asteroid)

        #   FPS
        self.clock = pygame.time.Clock()

    def main_loop(self):
        while True:
            self.clock.tick(60)
            self.refresh_asteroids()
            self._handle_inputs()
            self._draw()
            self._process_game_logic()

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects

    def _init_pygame(self):
        self.game_active = self.game_active
        pygame.init()
        pygame.display.set_caption("Cookie Comet")

    def title_screen(self):
        if not self.game_active:
            title_font = pygame.font.SysFont('arial', 100)
            title_text = title_font.render("Asteroids", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(self.W/2, self.H/2))
            self.screen.blit(title_text, title_rect)

    def refresh_asteroids(self):
        if len(self.big_asteroids) < 4:
            self.asteroids.append(Asteroid((get_random_position(self.screen)), self.asteroids.append))
            self.big_asteroids.append(self.asteroids[-1])

    def _handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

            if self.spaceship and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.game_active:
                self.spaceship.shoot()

            if not self.game_active and event.type == pygame.KEYDOWN:
                self.game_active = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.show_mask = not self.show_mask

        keys_pressed = pygame.key.get_pressed()

        if self.spaceship:
            if keys_pressed[pygame.K_d]:
                self.spaceship.rotate(clockwise=True)
            if keys_pressed[pygame.K_a]:
                self.spaceship.rotate(clockwise=False)
            if keys_pressed[pygame.K_w]:
                self.spaceship.accelerate()

    def reset(self):
        self.spaceship = Spaceship((self.W / 2, self.H / 2), self.bullets.append)
        self.asteroids.clear()
        self.big_asteroids.clear()
        self.bullets.clear()
        self.refresh_asteroids()

    def _process_game_logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if self.spaceship.collides_with(asteroid):
                    self.spaceship = None
                    pygame.time.delay(2000)
                    self.game_active = False
                    self.reset()
                    break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids:
                if bullet.collides_with(asteroid):
                    self.asteroids.remove(asteroid)
                    if asteroid.size == 3:
                        self.big_asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

    def _draw(self):
        self.screen.blit(self.background, (0, 0))

        if self.game_active:
            if not self.show_mask:
                for game_object in self._get_game_objects():
                    game_object.draw(self.screen)
            else:
                for game_object in self._get_game_objects():
                    game_object.other_draw(self.screen)

        else:
            self.title_screen()
        pygame.display.update()
