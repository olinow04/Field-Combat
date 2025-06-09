import pygame
import random
from src.game.unit import Unit
from src.game.bullet import Bullet

class AlliedUnit(Unit):
    """
    Klasa sojuszników gracza (przechwyconych lub przywołanych)
    Typy jednostek: infantry, tank, helicopter
    """

    TYPE_STATS = {
        "infantry": {
            "shoot_interval": 100,
            "bullet_speed": 5,
            "speed" : 2
        },
        "tank": {
            "shoot_interval": 90,
            "bullet_speed": 4,
            "speed": 1.3

        },
        "helicopter": {
            "shoot_interval": 60,
            "bullet_speed": 6,
            "speed": 3
        },
    }

    def __init__(self, position, unit_type, target_group, bullet_group, sprite=None):
        stats = self.TYPE_STATS.get(unit_type, self.TYPE_STATS["infantry"])
        self.speed = stats["speed"]
        used_sprite = sprite if sprite is not None else pygame.Surface((30, 30), pygame.SRCALPHA)
        super().__init__(position, used_sprite)
        self.type = unit_type
        self.target_group = target_group
        self.bullet_group = bullet_group
        self.shoot_timer = 0
        self.shoot_interval = stats["shoot_interval"]
        self.bullet_speed = stats["bullet_speed"]

        # Dla helikoptera: stan i zmienne ruchu
        if self.type == "helicopter":
            self.state = "APPROACH"
            self.SPEED = 4
            self.CLOSE_DIST = 180
            self.MAX_SHOTS = 3
            self.ESCAPE_SPEED = 6
            self.shot_counter = 0
            self.attack_time = 0

    def update(self):
        if self.type == "helicopter":
            self._update_helicopter()
        else:
            # only non-infantry units move toward targets
            if self.type != "infantry":
                self._move_towards_enemy()
            else:
                # infantry stands still
                self.velocity = pygame.math.Vector2(0, 0)

            self._update_standard()
        super().update()

    def _move_towards_enemy(self):
        if not self.target_group:
            self.velocity = pygame.math.Vector2(0, 0)
            return
        enemies = self.target_group.sprites()
        target = min(
            enemies,
            key=lambda e: pygame.math.Vector2(e.rect.center).distance_to(self.rect.center)
        )
        vec = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
        if vec.length() > 0:
            self.velocity = vec.normalize() * self.speed

    def _update_standard(self):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval and self.target_group:
            self.shoot_timer = 0
            target = random.choice(self.target_group.sprites())
            vec = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
            if vec.length() > 0:
                direction = vec.normalize()
                bullet = Bullet(
                    self.rect.center,
                    self._make_bullet_sprite(),
                    direction * self.bullet_speed
                )
                self.bullet_group.add(bullet)

    def _update_helicopter(self):
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()
            return

        if len(self.target_group) > 0:
            target = random.choice(self.target_group.sprites())
        else:
            target = None

        if self.state == "APPROACH" and target:
            delta = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
            dist = delta.length()
            if dist > 0:
                self.velocity = delta.normalize() * self.SPEED
            if dist < self.CLOSE_DIST:
                self.state = "ATTACK"
                self.velocity = pygame.math.Vector2(0, 0)
                self.attack_time = 0
                self.shot_counter = 0
        elif self.state == "ATTACK" and target:
            self.velocity = pygame.math.Vector2(0, 0)
            self.attack_time += 1
            if self.attack_time % 30 == 0:
                self._shoot_at_target(target)
                self.shot_counter += 1
            if self.shot_counter >= self.MAX_SHOTS:
                self.state = "ESCAPE"
                self.velocity = pygame.math.Vector2(random.choice([-1, 1]) * self.SPEED, -self.ESCAPE_SPEED)
        elif self.state == "ESCAPE":
            self.velocity.y -= 0.2

    def _shoot_at_target(self, target):
        current_pos = pygame.math.Vector2(self.rect.center)
        target_pos = pygame.math.Vector2(target.rect.center)
        direction = (target_pos - current_pos).normalize()
        bullet = Bullet(
            self.rect.center,
            self._make_bullet_sprite(),
            direction * 7
        )
        self.bullet_group.add(bullet)

    def _make_bullet_sprite(self):
        # Prosty biały pocisk (6x6 px)
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255), (3, 3), 3)
        return surf
