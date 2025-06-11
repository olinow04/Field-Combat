# game/enemy.py

import pygame                           # importujemy pygame do obsługi grafiki i wektorów
import random                           # importujemy moduł random do losowych wyborów
from .unit import Unit                  # importujemy klasę bazową Unit dla wspólnych cech jednostek
from .bullet import Bullet              # importujemy klasę Bullet reprezentującą pocisk

class Enemy(Unit):                       # definiujemy klasę bazową wszystkich wrogów, dziedziczy po Unit
    """Bazowa klasa dla wszystkich przeciwników w grze."""
    SPEED = 2                            # domyślna prędkość ruchu wroga

    def __init__(self, position, sprite, bullet_sprite=None):
        super().__init__(position, sprite)               # inicjalizujemy Unit: pozycja i obraz
        self.velocity = pygame.math.Vector2(0, 0)         # wektor prędkości, na początku zerowy
        self.bullet_sprite = bullet_sprite

    def update(self):
        # przesuwamy prostokąt (rect) o wektor prędkości
        self.rect.move_ip(self.velocity)


class Shooter(Enemy):                    # wróg, który strzela w stronę gracza w stałych odstępach
    """Strzelec - wróg strzelający w kierunku gracza w regularnych odstępach czasu."""
    def __init__(self, position, sprite, target, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)               # inicjalizacja pozycji i sprite
        self.target = target                              # obiekt gracza, w stronę którego strzelamy
        self.bullet_group = bullet_group                  # grupa, do której dodajemy wystrzelone pociski
        self.timer = 0                                    # licznik klatek od startu
        self.interval = 130                               # co ile klatek oddajemy strzał (≈2,16 s przy 60 FPS)

    def update(self):
        self.timer += 1                                   # zwiększamy licznik klatek
        # co dokładnie interval klatek wystrzelimy pocisk
        if self.timer % self.interval == 0:
            # obliczamy wektor od wroga do gracza
            delta = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if delta.length() > 0:
                direction = delta.normalize()             # normalizujemy wektor, aby miał długość 1
                bullet = Bullet(
                    self.rect.center,                     # startowa pozycja pocisku: środek wroga
                    self.make_bullet_sprite(),            # grafika pocisku
                    direction * 5                         # prędkość: kierunek * 5 pikseli/klatkę
                )
                self.bullet_group.add(bullet)             # dodajemy pocisk do grupy
        super().update()                                 # przesuwamy wroga zgodnie z velocity

    def make_bullet_sprite(self):
        if self.bullet_sprite:
            return self.bullet_sprite
        # Fallback do starego kółka jeśli nie ma sprite'a
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 255, 255), (3, 3), 3)
        return surf

class Chaser(Enemy):
    def __init__(self, position, sprite, target, bullet_group, enemy_type="infantry", bullet_sprite=None):
        super().__init__(position, sprite,  bullet_sprite)
        self.enemy_type = enemy_type
        self.target = target
        self.bullet_group = bullet_group

        # Statystyki wg typu jednostki
        if self.enemy_type == "tank":
            self.hp = 2
            self.speed = 1.3
            self.attack_interval = 90  # co 1.5 sekundy (60 FPS)
            self.last_attack = 0
            self.bullet_speed = 4
        else:  # infantry
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
        # Unikanie pocisków tylko dla infantry
        dodge_vector = pygame.math.Vector2(0, 0)
        if self.enemy_type == "infantry":
            min_dist = 80
            for bullet in self.bullet_group:
                bullet_vec = pygame.math.Vector2(bullet.rect.center) - pygame.math.Vector2(self.rect.center)
                if 0 < bullet_vec.length() < min_dist:
                    if abs(bullet_vec.angle_to(bullet.velocity)) > 150:
                        dodge = pygame.math.Vector2(-bullet_vec.y, bullet_vec.x).normalize()
                        dodge_vector += dodge

        # Losowa zmiana kierunku poziomego
        self.horizontal_timer += 1
        if self.horizontal_timer > self.horizontal_change_timer:
            self.horizontal_dir *= -1
            self.horizontal_change_timer = random.randint(60, 180)
            self.horizontal_timer = 0

        # Logika ruchu
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

                # Atak dla czołgów
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
        """Strzelanie tylko dla czołgów"""
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
        if self.bullet_sprite:
            return self.bullet_sprite
        # Fallback do kolorowych kółek
        color = (255, 0, 0) if self.enemy_type == "tank" else (0, 255, 0)
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (3, 3), 3)
        return surf

class Helicopter(Enemy):                 # szybki wróg, który zmienia stan: podejście, atak, ucieczka
    """Helikopter - zbliża się po skosie, atakuje z bliska, potem ucieka."""
    SPEED = 3                             # prędkość podejścia
    CLOSE_DIST = 180                     # odległość, przy której zaczyna atak
    MAX_SHOTS = 3                        # ile strzałów odda w fazie ataku
    ESCAPE_SPEED = 5# prędkość ucieczki w fazie ESCAPE

    def __init__(self, position, sprite, target, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)               # inicjalizacja Unit
        self.target = target                              # obiekt gracza
        self.bullet_group = bullet_group                  # grupa pocisków
        self.shot_counter = 0                             # licznik oddanych strzałów
        self.state = "APPROACH"                           # początkowy stan: zbliżanie
        self.attack_time = 0                              # licznik czasu w fazie ataku

    def update(self):
        # pobieramy prostokąt ekranu, by sprawdzać, czy helicopter nadal na ekranie
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()                                    # usuwamy, jeśli wyleciał poza ekran
            return

        # przełączamy zachowanie w zależności od aktualnego stanu
        if self.state == "APPROACH":
            self._approach_player()
        elif self.state == "ATTACK":
            self._attack_player()
        elif self.state == "ESCAPE":
            self._escape_pattern()

        super().update()                                  # przesuwamy helikopter

    def _approach_player(self):
        # faza zbliżania: leci w stronę gracza
        delta = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        dist = delta.length()
        if dist > 0:
            self.velocity = delta.normalize() * self.SPEED
        # gdy znajdzie się bliżej niż CLOSE_DIST, przechodzi do fazy ataku
        if dist < self.CLOSE_DIST:
            self.state = "ATTACK"
            self.velocity = pygame.math.Vector2(0, 0)      # zatrzymuje się
            self.attack_time = 0
            self.shot_counter = 0

    def _attack_player(self):
        # faza ataku: stoi w miejscu i co 30 klatek strzela
        self.velocity = pygame.math.Vector2(0, 0)
        self.attack_time += 1
        if self.attack_time % 30 == 0:
            self._shoot_at_player()                        # oddaje strzał
            self.shot_counter += 1
            # po MAX_SHOTS strzałach przechodzi do ucieczki
            if self.shot_counter >= self.MAX_SHOTS:
                self.state = "ESCAPE"
                # nadaje wstępny wektor ucieczki: w bok i w górę
                self.velocity = pygame.math.Vector2(
                    random.choice([-1, 1]) * self.SPEED,
                    -self.ESCAPE_SPEED
                )

    def _escape_pattern(self):
        # faza ucieczki: przyspiesza w górę (ujemna składowa y)
        self.velocity.y -= 0.2

    def _shoot_at_player(self):
        # obliczamy pozycję gracza i przewidujemy, gdzie będzie
        target_pos = pygame.math.Vector2(self.target.rect.center)
        current_pos = pygame.math.Vector2(self.rect.center)
        distance = target_pos - current_pos
        prediction = distance.length() / 10               # przewidywany czas lotu pocisku
        # pobieramy wektor prędkości gracza, jeśli istnieje
        player_vel = getattr(self.target, 'velocity', pygame.math.Vector2(0, 0))
        predicted_pos = target_pos + player_vel * prediction
        direction = (predicted_pos - current_pos).normalize()
        bullet = Bullet(
            self.rect.center,
            self._create_bullet_sprite(),
            direction * 7                                 # prędkość pocisku w fazie helikoptera
        )
        self.bullet_group.add(bullet)

    def _create_bullet_sprite(self):
        if self.bullet_sprite:
            return self.bullet_sprite
        # Fallback do czerwonego kółka
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 50, 50), (4, 4), 4)
        return surf

class Captor(Enemy):
    """
    UFO (Captor) – ma 20 punktów życia, nie ginie od beam,
    nie można go przechwycić. Po MAX_HP trafieniach zostaje zniszczony.
    """
    SPEED = 3
    SHOOT_INTERVAL = 120
    MAX_HP = 10                          # ile trafień wytrzymuje

    def __init__(self, position, sprite, allies_group, bullet_group, bullet_sprite=None):
        super().__init__(position, sprite, bullet_sprite)               # inicjalizacja pozycji i sprite
        self.allies_group = allies_group                  # grupa sojuszników, których ma porywać
        self.bullet_group = bullet_group                  # grupa, do której dodaje pociski
        self.timer = 0                                    # licznik klatek od startu
        self.carried = None                               # chwilowo nie niesie nikogo
        self.hp = self.MAX_HP                             # punkty życia UFO

    def update(self):
        self.timer += 1                                   # zwiększamy licznik klatek
        screen_rect = pygame.display.get_surface().get_rect()

        # jeśli nie ma już sojuszników, po prostu odlatuje w dół i znika
        if not self.allies_group or len(self.allies_group) == 0:
            self.velocity = pygame.math.Vector2(0, self.SPEED)
            super().update()
            if not screen_rect.colliderect(self.rect):
                self.kill()
            return

        # jeśli jeszcze nic nie porwał, to szuka najbliższego sojusznika
        if self.carried is None:
            ally = min(
                self.allies_group.sprites(),
                key=lambda u: pygame.math.Vector2(u.rect.center).distance_to(self.rect.center)
            )
            delta = pygame.math.Vector2(ally.rect.center) - pygame.math.Vector2(self.rect.center)
            if delta.length() > 0:
                self.velocity = delta.normalize() * self.SPEED
            super().update()
            # jeśli zetknie się z sojusznikiem, porywa go
            if pygame.sprite.collide_rect(self, ally):
                self.carried = ally
                self.allies_group.remove(ally)
        else:
            # gdy już porywa sojusznika, leci pionowo w górę razem z nim
            self.velocity = pygame.math.Vector2(0, -self.SPEED)
            super().update()
            self.carried.rect.center = self.rect.center
            # gdy wyleci poza ekran, niszczy i siebie, i porwanego
            if not screen_rect.colliderect(self.rect):
                self.carried.kill()
                self.kill()

        # dodatkowo, jeśli nie porywa nikogo, a wyleci poza ekran, usuwa się
        if self.carried is None and not screen_rect.colliderect(self.rect):
            self.kill()

    def make_bullet_sprite(self):
        if self.bullet_sprite:
            return self.bullet_sprite
        # Fallback do fioletowego kółka
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 255), (3, 3), 3)
        return surf

    def take_damage(self, dmg=1):
        """Zmniejsza życie UFO o wartość dmg. Jeśli hp ≤ 0, niszczy UFO."""
        self.hp -= dmg                                  # odejmujemy punkty życia
        if self.hp <= 0:
            if self.carried is not None:
                self.carried.kill()                     # jeśli coś porwał, upuszcza go (usuwa)
            self.kill()                                 # usuwa samo UFO

    def kill(self):
        """Usuwa UFO z gry."""
        super().kill()                                  # wywołujemy oryginalną metodę kill