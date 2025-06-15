import pygame

class Unit(pygame.sprite.Sprite):
    def __init__(self, position, sprite):
        # Inicjalizuje jednostkę z pozycją, obrazem i wektorem prędkości.
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        # Aktualizuje pozycję jednostki na podstawie jej prędkości.
        self.rect.move_ip(self.velocity)

    def draw(self, surface):
        # Rysuje jednostkę na podanej powierzchni.
        surface.blit(self.image, self.rect)
