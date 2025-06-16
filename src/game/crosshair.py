import pygame
import os


class Crosshair(pygame.sprite.Sprite):
    """Klasa wczytująca i opisująca zachowanie celownika"""
    def __init__(self, position):
        # Inicjalizuje celownik z określoną pozycją i wczytuje jego grafikę.
        super().__init__()

        # Wczytuje grafikę crosshair.png
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        image_dir = os.path.join(project_root, 'image')


        self.image = pygame.image.load(os.path.join(image_dir, 'crosshair.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))


        self.rect = self.image.get_rect()
        self.rect.center = position
        self.player = None

    def update(self):
        # Aktualizuje pozycję celownika względem gracza, jeśli jest przypisany.
        if hasattr(self, 'player') and self.player is not None:
            self.rect.center = self.player.rect.center + pygame.math.Vector2(0, -150)

    def draw(self, screen):
        # Rysuje celownik na ekranie w aktualnej pozycji.
        screen.blit(self.image, self.rect)