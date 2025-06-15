import pygame
from src.game.unit import Unit
from src.game.explosion import Explosion


class Bullet(Unit):
    def __init__(self, position, sprite, velocity):
        # Inicjalizuje pocisk z pozycją, grafiką i wektorem prędkości
        super().__init__(position, sprite)
        self.velocity = pygame.math.Vector2(velocity)

    def update(self):
        # Aktualizuje pozycję pocisku i usuwa go, jeśli wyleci poza ekran
        self.rect.move_ip(self.velocity)
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()


class PlayerBullet(Bullet):
    def __init__(self, position, sprite, velocity, crosshair, explosions_group):
        # Inicjalizuje pocisk gracza, cel (celownik) oraz grupę eksplozji
        super().__init__(position, sprite, velocity)
        self.crosshair = crosshair
        self.target_pos = pygame.math.Vector2(crosshair.rect.center)
        self.explosions_group = explosions_group
        self.has_exploded = False

    def update(self):
        # Aktualizuje pozycję pocisku, tworzy eksplozję po dotarciu do celu i usuwa pocisk
        super().update()
        if not self.has_exploded:
            current_pos = pygame.math.Vector2(self.rect.center)
            if current_pos.distance_to(self.target_pos) < 10:
                explosion = Explosion(self.target_pos)
                self.explosions_group.add(explosion)
                self.has_exploded = True
                self.kill()
