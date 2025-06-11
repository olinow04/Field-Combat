# game/player.py

import pygame  # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń
from src.game.unit import Unit  # importujemy klasę bazową Unit
from src.game.bullet import PlayerBullet  # importujemy klasę PlayerBullet reprezentującą pocisk gracza


class Player(Unit):  # definiujemy klasę gracza dziedziczącą po Unit
    SPEED = 3  # stała prędkość ruchu gracza (piksele na klatkę)

    def __init__(self, position, sprite, bullet_sprite):
        """
        :param position: początkowa pozycja gracza (tuple x,y)
        :param sprite: obrazek gracza (pygame.Surface)
        :param bullet_sprite: obrazek pocisku (pygame.Surface)
        """
        super().__init__(position, sprite)  # wywołujemy konstruktor Unit z pozycją i grafiką
        self.velocity = pygame.math.Vector2(0, 0)  # wektor prędkości, na początku zerowy
        self.hp = 4  # punkty życia gracza
        self.bullet_sprite = bullet_sprite  # zapisujemy sprite pocisku
        self.crosshair = None  # referencja do celownika, ustawiana później

    def handle_input(self):
        """Obsługa sterowania z klawiatury"""
        keys = pygame.key.get_pressed()  # pobieramy stan wszystkich klawiszy
        self.velocity = pygame.math.Vector2(0, 0)  # zerujemy wektor prędkości przed każdą aktualizacją

        # poruszanie w lewo i prawo
        if keys[pygame.K_LEFT]:
            self.velocity.x = -self.SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity.x = self.SPEED

        # poruszanie w górę i dół
        if keys[pygame.K_UP]:
            self.velocity.y = -self.SPEED
        if keys[pygame.K_DOWN]:
            self.velocity.y = self.SPEED

    def shoot(self):
        """Tworzy nowy pocisk gracza"""
        if self.crosshair is None:
            return None

        return PlayerBullet(
            self.rect.center,
            self.bullet_sprite,
            pygame.math.Vector2(0, -10),
            self.crosshair
        )

    def update(self):
        """Aktualizacja pozycji gracza"""
        self.handle_input()
        self.rect.move_ip(self.velocity)

        # ograniczenie gracza do obszaru ekranu
        screen_rect = pygame.display.get_surface().get_rect()
        self.rect.clamp_ip(screen_rect)