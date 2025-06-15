# game/enemy.py

import pygame
import random
from .unit import Unit
from .bullet import Bullet

class Enemy(Unit):
    SPEED = 2

    def __init__(self, position, sprite, bullet_sprite=None):
        super().__init__(position, sprite)
        self.velocity = pygame.math.Vector2(0, 0)
        self.bullet_sprite = bullet_sprite
        # Zmniejsz rect, aby kolizje były precyzyjne
        self.rect = self.image.get_rect(center=position).inflate(-30, -30)

class Shooter(Enemy):
    def __init__(self, position, sprite, target, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)
        self.target = target
        self.bullet_group = bullet_group
        self.timer = 0
        self.interval = 180

    def update(self):
        self.timer += 1
        if self.timer % self.interval == 0:
            delta = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if delta.length() > 0:
                direction = delta.normalize()
                bullet = Bullet(
                    self.rect.center,
                    self.make_bullet_sprite(),
                    direction * 5
                )
                self.bullet_group.add(bullet)
        super().update()

    def make_bullet_sprite(self):
        if self.bullet_sprite: return self.bullet_sprite

class Chaser(Enemy):
    def __init__(self, position, sprite, target, bullet_group, enemy_type="infantry", bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)
        self.enemy_type = enemy_type
        self.target = target
        self.bullet_group = bullet_group
        # Statystyki wg typu jednostki
        if self.enemy_type == "tank":
            self.hp = 2
            self.speed = 1.3
            self.attack_interval = 90
            self.last_attack = 0
            self.bullet_speed = 4
        else: # infantry
            self.hp = 1
            self.speed = random.uniform(1.8, 2.5)
        # Wspólne parametry
        self.pause_time = random.randint(40, 90)
        self.move_time = random.randint(60, 140)
        self.timer = 0
        self.paused = False
        self.horizontal_dir = random.choice([-1, 1])
        self.horizontal_change_timer = random.randint(60, 180)
        self.horizontal_timer = 0

    def update(self):
        dodge_vector = pygame.math.Vector2(0, 0)
        if self.enemy_type == "infantry":
            min_dist = 80
            for bullet in self.bullet_group:
                bullet_vec = pygame.math.Vector2(bullet.rect.center) - pygame.math.Vector2(self.rect.center)
                if 0 < bullet_vec.length() < min_dist:
                    if abs(bullet_vec.angle_to(bullet.velocity)) > 150:
                        dodge = pygame.math.Vector2(-bullet_vec.y, bullet_vec.x).normalize()
                        dodge_vector += dodge
        self.horizontal_timer += 1
        if self.horizontal_timer > self.horizontal_change_timer:
            self.horizontal_dir *= -1
            self.horizontal_change_timer = random.randint(60, 180)
            self.horizontal_timer = 0
        self.timer += 1
        if self.paused:
            self.velocity = pygame.math.Vector2(0, 0)
            if self.timer > self.pause_time:
                self.paused = False
                self.timer = 0
                self.move_time = random.randint(60, 140)
        else:
            to_player = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if to_player.length() > 0:
                move_vec = to_player.normalize() * self.speed
                move_vec.x += self.horizontal_dir * (0.8 if self.enemy_type == "tank" else 1.3)
                if self.enemy_type == "infantry" and dodge_vector.length() > 0:
                    move_vec += dodge_vector.normalize() * 2.5
                self.velocity = move_vec
            if self.enemy_type == "tank":
                self.last_attack += 1
                if self.last_attack >= self.attack_interval:
                    self._shoot()
                    self.last_attack = 0
            if self.timer > self.move_time:
                self.paused = True
                self.timer = 0
                self.pause_time = random.randint(40, 90)
        super().update()

    def _shoot(self):
        if self.enemy_type == "tank":
            direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                direction = direction.normalize()
                bullet = Bullet(
                    self.rect.center,
                    self._create_bullet_sprite(),
                    direction * self.bullet_speed
                )
                self.bullet_group.add(bullet)

    def _create_bullet_sprite(self):
        if self.bullet_sprite: return self.bullet_sprite
        color = (255, 0, 0) if self.enemy_type == "tank" else (0, 255, 0)
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (3, 3), 3)
        return surf

class Helicopter(Enemy):
    SPEED = 3
    CLOSE_DIST = 180
    MAX_SHOTS = 3
    ESCAPE_SPEED = 5

    def __init__(self, position, sprite, target, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)
        self.target = target
        self.bullet_group = bullet_group
        self.shot_counter = 0
        self.state = "APPROACH"
        self.attack_time = 0

    def update(self):
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect): self.kill(); return
        if self.state == "APPROACH": self._approach_player()
        elif self.state == "ATTACK": self._attack_player()
        elif self.state == "ESCAPE": self._escape_pattern()
        super().update()

    def _approach_player(self):
        delta = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        dist = delta.length()
        if dist > 0:
            self.velocity = delta.normalize() * self.SPEED
        if dist < self.CLOSE_DIST:
            self.state = "ATTACK"
            self.velocity = pygame.math.Vector2(0, 0)
            self.attack_time = 0
            self.shot_counter = 0

    def _attack_player(self):
        self.velocity = pygame.math.Vector2(0, 0)
        self.attack_time += 1
        if self.attack_time % 30 == 0:
            self._shoot_at_player()
            self.shot_counter += 1
        if self.shot_counter >= self.MAX_SHOTS:
            self.state = "ESCAPE"
            self.velocity = pygame.math.Vector2(
                random.choice([-1, 1]) * self.SPEED,
                -self.ESCAPE_SPEED
            )

    def _escape_pattern(self):
        self.velocity.y -= 0.2

    def _shoot_at_player(self):
        target_pos = pygame.math.Vector2(self.target.rect.center)
        current_pos = pygame.math.Vector2(self.rect.center)
        distance = target_pos - current_pos
        prediction = distance.length() / 10
        player_vel = getattr(self.target, 'velocity', pygame.math.Vector2(0, 0))
        predicted_pos = target_pos + player_vel * prediction
        direction = (predicted_pos - current_pos).normalize()
        bullet = Bullet(
            self.rect.center,
            self._create_bullet_sprite(),
            direction * 7
        )
        self.bullet_group.add(bullet)

    def _create_bullet_sprite(self):
        if self.bullet_sprite: return self.bullet_sprite
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 50, 50), (4, 4), 4)
        return surf

class Captor(Enemy):
    SPEED = 3
    MAX_HP = 5

    def __init__(self, position, sprite, allies_group, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)
        self.allies_group = allies_group
        self.bullet_group = bullet_group
        self.timer = 0
        self.carried = None
        self.hp = self.MAX_HP

    def update(self):
        self.timer += 1
        screen_rect = pygame.display.get_surface().get_rect()
        if not self.allies_group or len(self.allies_group) == 0:
            self.velocity = pygame.math.Vector2(0, self.SPEED)
            super().update()
            if not screen_rect.colliderect(self.rect): self.kill(); return
        if self.carried is None:
            ally = min(
                self.allies_group.sprites(),
                key=lambda u: pygame.math.Vector2(u.rect.center).distance_to(self.rect.center)
            )
            delta = pygame.math.Vector2(ally.rect.center) - pygame.math.Vector2(self.rect.center)
            if delta.length() > 0:
                self.velocity = delta.normalize() * self.SPEED
            super().update()
            if pygame.sprite.collide_rect(self, ally):
                self.carried = ally
                self.allies_group.remove(ally)
        else:
            self.velocity = pygame.math.Vector2(0, -self.SPEED)
            super().update()
            self.carried.rect.center = self.rect.center
            if not screen_rect.colliderect(self.rect):
                self.carried.kill()
                self.kill()
        if self.carried is None and not screen_rect.colliderect(self.rect): self.kill()

    def make_bullet_sprite(self):
        if self.bullet_sprite: return self.bullet_sprite
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 255), (3, 3), 3)
        return surf

    def take_damage(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0:
            if self.carried is not None: self.carried.kill()
            self.kill()
