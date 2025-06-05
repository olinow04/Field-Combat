# level.py

import pygame
import random
import os

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from .player import Player
from .enemy import Shooter, Chaser, Captor, Helicopter
from .crosshair import Crosshair
from .beam import Beam
from .allied_unit import AlliedUnit

PORTAL_WIDTH = 60
PORTAL_HEIGHT = 40
PORTAL_COLOR = (255, 0, 255)
PORTAL_Y = 10

class Level:
    REINFORCEMENT_TYPES = [
        "infantry", "tank", "artillery",
        "helicopter", "infantry", "tank"
    ]

    def __init__(self, screen, number, score_manager, bg_color=None):
        self.screen = screen
        self.number = number
        self.score_manager = score_manager
        #
        # # ----- ŁADOWANIE GRAFIK -----
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        image_dir = os.path.join(project_root, 'image')
        # Główne postacie
        self.genesis_img = pygame.image.load(os.path.join(image_dir, 'genesis.png')).convert_alpha()
        self.enemy_helicopter_img = pygame.image.load(os.path.join(image_dir, 'enemy_helicopter.png')).convert_alpha()
        self.enemy_solider_img = pygame.image.load(os.path.join(image_dir, 'enemy_solider.png')).convert_alpha()
        self.ally_solider_img = pygame.image.load(os.path.join(image_dir, 'ally_solider.png')).convert_alpha()
        # (opcjonalnie skalowanie, np. do 30x30 px)
        self.genesis_img = pygame.transform.scale(self.genesis_img, (80, 80))
        self.enemy_helicopter_img = pygame.transform.scale(self.enemy_helicopter_img, (80, 80))
        self.enemy_solider_img = pygame.transform.scale(self.enemy_solider_img, (80, 80))
        self.ally_solider_img = pygame.transform.scale(self.ally_solider_img, (80, 80))

        # Inicjalizacja gracza (Genesis)
        self.player = Player(
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
            self.genesis_img
        )
        self.player.hp = 10

        self.crosshair = Crosshair(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.ally_bullets = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        self.allies = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.reinforcement_queue = list(self.REINFORCEMENT_TYPES)
        self._space_pressed = False
        self._b_pressed = False
        self._c_pressed = False
        self.frame_count = 0
        self.captor_spawned = False
        self.captor_spawn_at = random.randint(60, 300)
        self.portal_active = False
        self.portal_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - PORTAL_WIDTH // 2,
            PORTAL_Y,
            PORTAL_WIDTH,
            PORTAL_HEIGHT
        )
        self.portal_timer = 0
        self.genesis_migrate = False
        self.bg_color = (30, 30, 30) if bg_color is None else bg_color
        self._spawn_enemies()
        self.score = 0

    def _create_sprite(self, color, size=(30, 30)):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    def _spawn_enemies(self):
        shooter_positions = [
            (SCREEN_WIDTH // 5 * 1, 100),
            (SCREEN_WIDTH // 5 * 2, 100),
            (SCREEN_WIDTH // 5 * 3, 100),
            (SCREEN_WIDTH // 5 * 4, 100)
        ]
        # Shooterzy (klasyczny czerwony prostokąt)
        for pos in shooter_positions:
            self.enemies.add(Shooter(
                pos,
                self._create_sprite((255, 0, 0)),
                self.player,
                self.enemy_bullets
            ))

        helicopter_positions = []
        num_helicopters = self.number
        spacing = SCREEN_WIDTH // (num_helicopters + 1)
        for h in range(num_helicopters):
            x = spacing * (h + 1)
            helicopter_positions.append((x, 40))

        for i in range(self.number * 3):
            x = 50 + (i * 70) % (SCREEN_WIDTH - 100)
            y = 150 + (i // 10) * 60
            if i % 5 == 4 and len(helicopter_positions) > 0:
                # HELIKOPTER: używamy grafiki alien_helicopter_img
                self.enemies.add(Helicopter(
                    helicopter_positions.pop(),
                    self.enemy_helicopter_img,
                    self.player,
                    self.enemy_bullets
                ))
            else:

                self.enemies.add(Chaser(
                    (x, y),
                    self.enemy_solider_img,
                    self.player,
                    self.bullets
                ))

    def run(self):
        clock = pygame.time.Clock()
        next_bg_color = self.bg_color
        while True:
            self.frame_count += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not keys[pygame.K_b]:
                if not self._space_pressed:
                    b = self.player.shoot()
                    if b:
                        self.bullets.add(b)
                    self._space_pressed = True
            else:
                self._space_pressed = False
            if keys[pygame.K_b] and not keys[pygame.K_SPACE]:
                if not self._b_pressed:
                    beam = Beam(self.player.rect.center, self.crosshair.rect.center)
                    self.beams.add(beam)
                    self._b_pressed = True
            else:
                self._b_pressed = False

            if keys[pygame.K_c]:
                if not self._c_pressed and self.reinforcement_queue and len(self.allies) < 6:
                    unit_type = self.reinforcement_queue.pop(0)
                    spawn_pos = (self.player.rect.centerx, self.player.rect.top - 30)
                    # PRZEKAZUJEMY GRAFIKĘ alien_solider_img tylko dla infantry
                    if unit_type == "infantry":
                        ally = AlliedUnit(spawn_pos, unit_type, self.enemies, self.ally_bullets, sprite=self.ally_solider_img)
                    else:
                        ally = AlliedUnit(spawn_pos, unit_type, self.enemies, self.ally_bullets)
                    self.allies.add(ally)
                    self._c_pressed = True
            else:
                self._c_pressed = False

            if not self.captor_spawned and self.frame_count >= self.captor_spawn_at and len(self.allies) > 0:
                pos = (random.randint(100, SCREEN_WIDTH - 100), 40)
                cap_spr = self._create_sprite((255, 255, 0), (30, 30))
                self.enemies.add(
                    Captor(pos, cap_spr, self.allies, self.enemy_bullets)
                )
                self.captor_spawned = True

            next_level, next_bg_color = self._update_logic()
            if next_level is None:
                return None
            elif next_level != self.number:
                return next_level, next_bg_color

            self._draw()
            pygame.display.flip()
            clock.tick(60)

    def _update_logic(self):
        self.player.update()
        self.crosshair.update()
        self.bullets.update()
        self.enemy_bullets.update()
        self.ally_bullets.update()
        self.beams.update()
        self.allies.update()
        self.enemies.update()

        # Kolizje pocisków gracza z wrogami
        for b in self.bullets:
            hits = pygame.sprite.spritecollide(b, self.enemies, False)
            for enemy in hits:
                if isinstance(enemy, Captor):
                    enemy.take_damage()
                    if enemy.hp <= 0:
                        self.score += 50  # UFO zniszczone
                elif isinstance(enemy, Shooter):
                    enemy.kill()
                    b.kill()
                    # brak punktów za Shooter!
                    continue
                else:
                    enemy.kill()
                    self.score += 10  # standardowy wróg
                b.kill()

        # Kolizje promienia z wrogami (przechwytywanie Chaserów)
        for beam in self.beams:
            hits = pygame.sprite.spritecollide(beam, self.enemies, False)
            for enemy in hits:
                if isinstance(enemy, Chaser):        # tylko Chaser można przechwycić
                    coord = enemy.rect.center
                    if len(self.allies) < 6:
                        ally = AlliedUnit(coord, "infantry", self.enemies, self.ally_bullets)
                        self.allies.add(ally)       # staje się nowym sojusznikiem
                        enemy.kill()                # usuwamy wroga
                        beam.kill()                 # usuwamy promień

        # Kolizje pocisków wrogów z graczem
        for b in self.enemy_bullets:
            if pygame.sprite.collide_rect(b, self.player):
                b.kill()
                self.player.hp -= 1                 # gracz traci życie
                if self.player.hp <= 0:
                    return None, self.bg_color      # koniec gry

        # Kolizje pocisków sojuszników z wrogami
        for b in self.ally_bullets:
            hits = pygame.sprite.spritecollide(b, self.enemies, False)
            for enemy in hits:
                if isinstance(enemy, Captor):
                    enemy.take_damage()
                    if enemy.hp <= 0:
                        self.score += 50
                elif isinstance(enemy, Shooter):
                    enemy.kill()
                    b.kill()
                    continue
                else:
                    enemy.kill()
                    self.score += 5  # sojusznik zabija – mniej punktów
                b.kill()

        # Kolizje wrogów z graczem przy bezpośrednim kontakcie
        for e in self.enemies:
            if pygame.sprite.collide_rect(e, self.player):
                return None, self.bg_color          # gracz ginie przy kontakcie

        # LOGIKA PORTALU ---
        if not self.portal_active:
            # sprawdzamy, czy wszyscy Shooterzy zostali pokonani
            shooters_alive = any(isinstance(e, Shooter) for e in self.enemies)
            if not shooters_alive:
                self.portal_active = True            # uruchamiamy portal

        # sprawdzenie, czy gracz wszedł w obszar portalu
        if self.portal_active and self.player.rect.colliderect(self.portal_rect):
            self.genesis_migrate = True
        if self.portal_timer > 120:
            next_bg_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            self.score += 1000  # bonus za ukończenie poziomu
            self.score_manager.save_score(self.score)
            return self.number + 1, next_bg_color

        # efekt migania gracza w portalu przed przeniesieniem
        if self.genesis_migrate:
            self.portal_timer += 1
            alpha = 128 + 127 * (self.portal_timer % 20 < 10)
            self.player.image.set_alpha(alpha)     # pulsująca przezroczystość
            if self.portal_timer > 120:            # po 2 sekundach
                next_bg_color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )                                  # losujemy nowy kolor tła
                self.score_manager.save_score(self.score)  # zapisujemy wynik
                return self.number + 1, next_bg_color
        else:
            self.player.image.set_alpha(255)        # pełna widoczność, jeśli nie w portalu

        return self.number, self.bg_color          # brak zmiany poziomu

    def _draw(self):
        self.screen.fill(self.bg_color)
        self.player.draw(self.screen)
        self.crosshair.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)
        self.ally_bullets.draw(self.screen)
        self.beams.draw(self.screen)
        self.allies.draw(self.screen)
        self.enemies.draw(self.screen)
        if self.portal_active:
            pygame.draw.rect(self.screen, PORTAL_COLOR, self.portal_rect, 3)
        font = pygame.font.SysFont("Arial", 24)
        score_surf = font.render(f"Wynik: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        allies_surf = font.render(f"Sojusznicy: {len(self.allies)}", True, (0, 255, 0))
        lives_surf = font.render(f"Życia: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(allies_surf, (10, 40))
        self.screen.blit(lives_surf, (10, 70))