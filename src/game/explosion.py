import pygame


class Explosion(pygame.sprite.Sprite):
    images = []

    def __init__(self, pos):
        # Inicjalizuje animację eksplozji w podanej pozycji.
        super().__init__()
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.frame_index = 0
        self.lifetime = 200

    def update(self):
        # Aktualizuje animację eksplozji i usuwa ją po zakończeniu.
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.images)
            center = self.rect.center
            self.image = self.images[self.frame_index]
            self.rect = self.image.get_rect(center=center)
            self.lifetime -= self.frame_rate
            if self.lifetime <= 0:
                self.kill()
