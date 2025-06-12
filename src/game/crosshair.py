import pygame
import os


class Crosshair(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        # Wczytaj grafikę crosshair.png zamiast żółtego kwadratu
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        image_dir = os.path.join(project_root, 'image')


        self.image = pygame.image.load(os.path.join(image_dir, 'crosshair.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))


        self.rect = self.image.get_rect()
        self.rect.center = position
        self.player = None

    def update(self):
        """Aktualizacja pozycji celownika względem gracza"""
        if hasattr(self, 'player') and self.player is not None:
            self.rect.center = self.player.rect.center + pygame.math.Vector2(0, -150)

    def draw(self, screen):
        """Rysuje celownik na podanej powierzchni"""
        screen.blit(self.image, self.rect)
