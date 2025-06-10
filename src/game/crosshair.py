# game/crosshair.py

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT


class Crosshair(pygame.sprite.Sprite):
    """Klasa reprezentująca celownik gracza"""

    def __init__(self, position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250),
                 size=32, color=(255, 255, 0)):
        """
        :param position: początkowa pozycja celownika (tuple x,y)
        :param size: rozmiar kwadratu celownika w pikselach
        :param color: kolor linii i kółka celownika (tuple r,g,b)
        """
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.size = size
        self.color = color
        self.player = None  # referencja do gracza, ustawiana później

        # tworzymy przezroczystą powierzchnię (surface)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # rysujemy ramkę kwadratu
        pygame.draw.rect(self.image, color, (0, 0, size, size), 1)
        # rysujemy linie krzyża
        pygame.draw.line(self.image, color, (0, size // 2), (size, size // 2), 1)
        pygame.draw.line(self.image, color, (size // 2, 0), (size // 2, size), 1)
        # rysujemy kółko w środku
        pygame.draw.circle(self.image, color, (size // 2, size // 2), 4)

        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        """Aktualizacja pozycji celownika względem gracza"""
        if hasattr(self, 'player') and self.player is not None:
            self.rect.center = self.player.rect.center + pygame.math.Vector2(0, -150)

    def draw(self, surface):
        """Rysuje celownik na podanej powierzchni"""
        surface.blit(self.image, self.rect)