import pygame
from src.game.unit import Unit
from src.game.bullet import PlayerBullet


class Player(Unit):
    SPEED = 3

    def __init__(self, position, sprite, bullet_sprite):
        # Inicjalizuje gracza z pozycją, sprite'em, prędkością i początkowym HP.
        super().__init__(position, sprite)
        self.velocity = pygame.math.Vector2(0, 0)
        self.hp = 4
        self.bullet_sprite = bullet_sprite
        self.crosshair = None

    def handle_input(self):
        # Obsługuje wejście z klawiatury, ustalając kierunek ruchu gracza.
        keys = pygame.key.get_pressed()
        self.velocity = pygame.math.Vector2(0, 0)

        if keys[pygame.K_LEFT]:
            self.velocity.x = -self.SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity.x = self.SPEED

        if keys[pygame.K_UP]:
            self.velocity.y = -self.SPEED
        if keys[pygame.K_DOWN]:
            self.velocity.y = self.SPEED

    def shoot(self):
        # Tworzy i zwraca nowy pocisk gracza, jeśli dostępny jest celownik.
        if self.crosshair is None:
            return None

        return PlayerBullet(
            self.rect.center,
            self.bullet_sprite,
            pygame.math.Vector2(0, -10),
            self.crosshair
        )

    def update(self):
        # Aktualizuje stan gracza: przetwarza ruch i ogranicza jego pozycję do ekranu.
        self.handle_input()
        self.rect.move_ip(self.velocity)
        screen_rect = pygame.display.get_surface().get_rect()
        self.rect.clamp_ip(screen_rect)
