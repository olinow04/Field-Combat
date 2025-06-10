
# game/bullet.py

import pygame                                       # importujemy bibliotekę pygame do obsługi grafiki i wektorów
from src.game.unit import Unit                     # importujemy klasę bazową Unit
from src.game.explosion import Explosion           # importujemy naszą własną klasę Explosion


class Bullet(Unit):                                 # definiujemy klasę Bullet dziedziczącą po Unit
    def __init__(self, position, sprite, velocity):
        """
        :param position: pozycja początkowa pocisku (tuple x,y)
        :param sprite: obrazek pocisku (pygame.Surface)
        :param velocity: wektor prędkości pocisku (tuple x,y)
        """
        super().__init__(position, sprite)          # wywołujemy konstruktor Unit
        self.velocity = pygame.math.Vector2(velocity)  # wektor prędkości jako Vector2

    def update(self):
        """Aktualizuje pozycję pocisku i sprawdza czy jest na ekranie"""
        self.rect.move_ip(self.velocity)
        # usuń pocisk, jeśli wyleciał poza ekran
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()


class PlayerBullet(Bullet):
    """Klasa reprezentująca pocisk gracza z eksplozją przy celu"""
    def __init__(self, position, sprite, velocity, crosshair, explosions_group):
        """
        :param position: pozycja początkowa pocisku (tuple x,y)
        :param sprite: obrazek pocisku (pygame.Surface)
        :param velocity: wektor prędkości pocisku (tuple x,y)
        :param crosshair: referencja do celownika
        :param explosions_group: grupa sprite'ów dla eksplozji
        """
        super().__init__(position, sprite, velocity)
        self.crosshair = crosshair
        self.target_pos = pygame.math.Vector2(crosshair.rect.center)
        self.explosions_group = explosions_group
        self.has_exploded = False  # flaga sprawdzająca czy już eksplodował

    def update(self):
        """Aktualizuje pozycję pocisku i sprawdza odległość od celu"""
        super().update()  # standardowa aktualizacja pocisku

        if not self.has_exploded:  # sprawdzamy czy pocisk jeszcze nie eksplodował
            # sprawdzamy odległość od celu
            current_pos = pygame.math.Vector2(self.rect.center)
            if current_pos.distance_to(self.target_pos) < 10:
                # tworzymy eksplozję w miejscu trafienia
                explosion = Explosion(self.target_pos)
                self.explosions_group.add(explosion)
                self.has_exploded = True  # oznaczamy, że pocisk już eksplodował
                self.kill()  # usuwamy pocisk
