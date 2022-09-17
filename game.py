import pygame
from utils import load_sprite, get_random_position, get_random_vel
from models import Spaceship, Asteroid, UFO
from os.path import exists
from random import randint


#   main game class
class CookieComet:
    MIN_ASTEROID_DISTANCE = 250
    P = (200, 100, 200)

    def __init__(self):

        #   pygame initialization
        self.game_active = False
        self.show_mask = False
        self._init_pygame()

        #   timers
        self.event_timer = pygame.USEREVENT + 0
        pygame.time.set_timer(self.event_timer, 2000)
        self.ufo_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ufo_timer, 3000)

        #   creating screen
        self.W, self.H = 1370, 710
        self.screen = pygame.display.set_mode((self.W, self.H))

        #   fonts
        self.msg_font = pygame.font.Font('graphics/other/ARCADE_N.TTF', 40)
        self.msg_text = self.msg_font.render("Press [Enter] to Play", True, self.P)
        self.msg_rect = self.msg_text.get_rect(topleft=(276, 433))

        self.title_font = pygame.font.Font('graphics/other/ARCADE_N.TTF', 100)
        self.title_text = self.title_font.render("Cookie Comet", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(self.W/2, self.H/2))

        self.cmd = 'up'
        self.gravity = 1

        #   scores
        self.score = 0

        if exists('saves.txt'):
            with open('saves.txt', 'r') as f:
                self.high_score = int(f.read())
        else:
            self.high_score = 0

        #   image loading
        self.cookie_icon = pygame.image.load('graphics/other/cookie-comet-icon.ico')
        pygame.display.set_icon(self.cookie_icon)
        self.background = load_sprite('other', 'milky-way-2695569__480', 'jpg', False)

        #   game objects
        self.bullets = []
        self.spaceship = Spaceship((self.W/2, self.H/2), self.bullets.append)
        self.asteroids = []
        self.big_asteroids = []
        self.ufos = []
        self.ufo_bullets = []

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

    def spawn_ufo(self):
        if self.score >= 2000:
            num = randint(0, 699)
            if num == 0:
                ufo = UFO(get_random_position(self.screen), get_random_vel(4, 4), self.ufo_bullets.append)
                self.ufos.append(ufo)

    def main_loop(self):
        while True:
            self.clock.tick(60)
            self.refresh_asteroids()
            self._handle_inputs()
            self._draw()
            self._process_game_logic()

    def show_score(self):

        if self.score >= self.high_score:
            self.high_score = self.score

        score_font = pygame.font.Font('graphics/other/ARCADE_N.TTF', 30)
        score_text = score_font.render(f'Score: {self.score}', True, 'white')
        score_rect = score_text.get_rect(topleft=(400, 5))
        high_text = score_font.render(f'High: {self.high_score}', True, 'white')
        high_rect = high_text.get_rect(topleft=(775, 5))

        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_text, high_rect)

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets, *self.ufos, *self.ufo_bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects

    def _init_pygame(self):
        self.game_active = self.game_active
        pygame.init()
        pygame.display.set_caption("Cookie Comet")

    def title_screen(self):

        self.msg_rect.y += int(self.gravity)

        if self.msg_rect.y > 463:
            self.gravity = -5

        self.gravity += 0.15

        help_font = pygame.font.Font('graphics/other/ARCADE_N.TTF', 20)
        help_text = help_font.render('Accelerate with [W], Rotate with [A], and [D], Shoot with [Space]', False, (255, 255, 255))
        help_rect = help_text.get_rect(center=(self.W/2, self.H - 60))

        self.screen.blit(help_text, help_rect)
        self.screen.blit(self.msg_text, self.msg_rect)
        self.screen.blit(self.title_text, self.title_rect)

    def refresh_asteroids(self):
        if len(self.big_asteroids) < 3:
            self.asteroids.append(Asteroid((get_random_position(self.screen)), self.asteroids.append))
            self.big_asteroids.append(self.asteroids[-1])

    def _handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

            if self.spaceship and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.game_active:
                self.spaceship.shoot()

            if not self.game_active and (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                self.score = 0
                self.game_active = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.show_mask = not self.show_mask

            if event.type == self.ufo_timer and len(self.ufos):
                for ufo in self.ufos:
                    ufo.shoot(self.spaceship)

        keys_pressed = pygame.key.get_pressed()

        if self.spaceship:
            if keys_pressed[pygame.K_d]:
                self.spaceship.rotate(clockwise=True)
            if keys_pressed[pygame.K_a]:
                self.spaceship.rotate(clockwise=False)
            if keys_pressed[pygame.K_w]:
                self.spaceship.accelerate()

    def save_score(self):
        with open('saves.txt', 'w') as f:
            f.write(str(self.score))

    def reset(self):
        self.spaceship = Spaceship((self.W / 2, self.H / 2), self.bullets.append)
        self.asteroids.clear()
        self.big_asteroids.clear()
        self.bullets.clear()
        self.ufos.clear()
        self.refresh_asteroids()

    def _process_game_logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            self.spawn_ufo()
            for asteroid in self.asteroids:
                if self.spaceship.collides_with(asteroid):
                    self.spaceship = None
                    if self.score >= self.high_score:
                        with open('saves.txt', 'w') as f:
                            f.write(str(self.score))
                    self.game_active = False
                    self.reset()
                    break

            for bullet in self.ufo_bullets:
                if self.spaceship.collides_with(bullet):
                    self.spaceship = None
                    if self.score >= self.high_score:
                        with open('saves.txt', 'w') as f:
                            f.write(str(self.score))
                    self.game_active = False
                    self.reset()
                    break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids:
                if bullet.collides_with(asteroid):
                    self.asteroids.remove(asteroid)
                    if asteroid.size == 3:
                        self.big_asteroids.remove(asteroid)
                        self.score += 20
                    if asteroid.size == 2:
                        self.score += 50
                    if asteroid.size == 1:
                        self.score += 100

                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

            for ufo in self.ufos:
                if ufo.collides_with(bullet):
                    self.score += 1000
                    self.bullets.remove(bullet)
                    self.ufos.remove(ufo)
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

        if not self.game_active:
            self.title_screen()

        self.show_score()
        pygame.display.update()
