import pygame
import random
from src.game.unit import Unit
from src.game.bullet import Bullet

class AlliedUnit(Unit):
    """
    Klasa sojuszników gracza (przechwyconych lub przywołanych)
    Typy jednostek: infantry, tank, helicopter

    Player's allied units (captured or summoned)
    Unit types: infantry, tank, helicopter
    """
    TYPE_STATS = {
        "infantry": {
            "shoot_interval": 100,   # co ile klatek strzela piechota
            "bullet_speed": 5,       # prędkość pocisku piechoty
            "speed": 2               # prędkość piechoty (nieużywana, bo piechota stoi)
        },
        "tank": {
            "shoot_interval": 90,    # co ile klatek strzela czołg
            "bullet_speed": 4,       # prędkość pocisku czołgu
            "speed": 1.3             # prędkość czołgu
        },
        "helicopter": {
            "shoot_interval": 60,    # co ile klatek strzela helikopter (nieużywane w _update_helicopter)
            "bullet_speed": 6,       # prędkość pocisku helikoptera (nieużywane w _update_helicopter)
            "speed": 3               # prędkość helikoptera (nieużywana, bo helikopter ma własny SPEED)
        }
    }

    def __init__(self, position, unit_type, target_group, bullet_group, bullet_sprite, sprite=None):
        """
        Inicjalizacja jednostki sojuszniczej.
        position: pozycja startowa (x, y)
        unit_type: typ jednostki ("infantry", "tank", "helicopter")
        target_group: grupa wrogów (pygame.sprite.Group)
        bullet_group: grupa pocisków (pygame.sprite.Group)
        bullet_sprite: sprite pocisku
        sprite: opcjonalny sprite jednostki
        """
        stats = self.TYPE_STATS.get(unit_type, self.TYPE_STATS["infantry"])
        self.speed = stats["speed"]
        used_sprite = sprite if sprite is not None else pygame.Surface((30, 30), pygame.SRCALPHA)
        super().__init__(position, used_sprite)
        self.type = unit_type
        self.target_group = target_group
        self.bullet_group = bullet_group
        self.shoot_timer = 0         # licznik czasu do kolejnego strzału
        self.shoot_interval = stats["shoot_interval"]
        self.bullet_speed = stats["bullet_speed"]
        self.bullet_sprite = bullet_sprite

        # Dla helikoptera: stan i zmienne ruchu
        if self.type == "helicopter":
            self.state = "APPROACH"  # stan początkowy: zbliżanie się
            self.SPEED = 4           # prędkość helikoptera
            self.CLOSE_DIST = 180    # minimalna odległość ataku
            self.MAX_SHOTS = 3       # maksymalna liczba strzałów w jednym ataku
            self.ESCAPE_SPEED = 5    # prędkość ucieczki
            self.shot_counter = 0    # licznik wykonanych strzałów
            self.attack_time = 0     # czas trwania ataku

    def update(self):
        """
        Aktualizacja stanu jednostki w każdej klatce gry.
        """
        if self.type == "helicopter":
            self._update_helicopter()
        else:
            # tylko jednostki inne niż piechota poruszają się w stronę wroga
            if self.type != "infantry":
                self._move_towards_enemy()
            else:
                # piechota stoi w miejscu
                self.velocity = pygame.math.Vector2(0, 0)
            self._update_standard()
        super().update()

    def _move_towards_enemy(self):
        """
        Poruszanie się w kierunku najbliższego wroga.
        """
        if not self.target_group:
            self.velocity = pygame.math.Vector2( 0, 0 )
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
        """
        Standardowa logika strzelania w każdej klatce gry (dla piechoty i czołgu).
        """
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
        """
        Specjalna logika aktualizacji dla helikoptera.
        """
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()  # usuń helikopter, jeśli opuścił ekran
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
            if self.attack_time % 30 == 0:  # strzał co 30 klatek
                self._shoot_at_target(target)
                self.shot_counter += 1
            if self.shot_counter >= self.MAX_SHOTS:
                self.state = "ESCAPE"
                self.velocity = pygame.math.Vector2(random.choice([-1, 1]) * self.SPEED, -self.ESCAPE_SPEED)

        elif self.state == "ESCAPE":
            self.velocity.y -= 0.2  # dodatkowe przyspieszenie w górę

    def _shoot_at_target(self, target):
        """
        Strzelanie do wybranego celu (specjalnie dla helikoptera).
        """
        current_pos = pygame.math.Vector2(self.rect.center)
        target_pos = pygame.math.Vector2(target.rect.center)
        direction = (target_pos - current_pos).normalize()
        bullet = Bullet(
            self.rect.center,
            self._make_bullet_sprite(),
            direction * 7  # prędkość pocisku helikoptera
        )
        self.bullet_group.add(bullet)

    def _make_bullet_sprite(self):
        """
        Tworzy sprite pocisku na podstawie przekazanego sprite'a.
        """
        return self.bullet_sprite
