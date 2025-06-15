import pygame
import os


class Crosshair(pygame.sprite.Sprite):
    def __init__(self, position):
        # Inicjalizuje celownik i ustawia jego pozycję oraz grafikę.
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
        # Aktualizuje pozycję celownika na podstawie pozycji myszy.
        mouse_pos = pygame.mouse.get_pos()
        self.rect.center = mouse_pos

    def draw(self, screen):
        # Rysuje celownik na ekranie.
        screen.blit(self.image, self.rect)
