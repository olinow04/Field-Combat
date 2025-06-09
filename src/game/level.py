# level.py

import pygame
import random
import os

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from .player import Player
from .enemy import Shooter, Chaser, Captor, Helicopter
from .crosshair import Crosshair
from .allied_unit import AlliedUnit

class Level:
    REINFORCEMENT_TYPES = [
        "infantry", "tank", "artillery", "helicopter",
        "infantry", "tank"
    ]

    def __init__(self, screen, number, score_manager, bg_color=None):
        self.screen = screen
        self.number = number
        self.score_manager = score_manager

        # ścieżka do obrazków
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        image_dir = os.path.join(project_root, 'image')

        # wczytanie sprite'ów
        self.genesis_img           = pygame.image.load(os.path.join(image_dir, 'genesis.png')).convert_alpha()
        self.enemy_helicopter_img  = pygame.image.load(os.path.join(image_dir, 'enemy_helicopter.png')).convert_alpha()
        self.enemy_solider_img     = pygame.image.load(os.path.join(image_dir, 'enemy_solider.png')).convert_alpha()
        self.enemy_tank_img        = pygame.image.load(os.path.join(image_dir, 'enemy_tank.png')).convert_alpha()
        self.ally_solider_img      = pygame.image.load(os.path.join(image_dir, 'ally_solider.png')).convert_alpha()
        self.ally_helicopter_img   = pygame.image.load(os.path.join(image_dir, 'ally_helicopter.png')).convert_alpha()
        self.ally_tank_img         = pygame.image.load(os.path.join(image_dir, 'ally_tank.png')).convert_alpha()
        self.captor_img            = pygame.image.load(os.path.join(image_dir, 'captor.png')).convert_alpha()
        self.shooter_img            = pygame.image.load(os.path.join(image_dir, 'shooter.png')).convert_alpha()
        self.bullet_img            = pygame.image.load(os.path.join(image_dir, 'bullet.png')).convert_alpha()
        self.field_imgs = {
            1: pygame.image.load(os.path.join(image_dir, 'field_1.png')).convert(),
            2: pygame.image.load(os.path.join(image_dir, 'field_2.png')).convert()
        }
        self.portal_img = pygame.image.load(os.path.join(image_dir, 'portal.png')).convert_alpha()
        # opcjonalne skalowanie do rozmiaru ekranu
        for lvl, img in self.field_imgs.items():
            self.field_imgs[lvl] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))


        # aliasy wrogich grafik (możesz zmienić na własne pliki alien_*.png)
        self.alien_helicopter_img = self.enemy_helicopter_img
        self.alien_solider_img    = self.enemy_solider_img

        # skalowanie do 80×80
        for attr in (
            'genesis_img', 'enemy_helicopter_img', 'enemy_solider_img', 'enemy_tank_img',
            'ally_solider_img', 'ally_helicopter_img', 'ally_tank_img',
            'alien_helicopter_img', 'alien_solider_img', 'captor_img', 'shooter_img', 'portal_img'
        ):
            img = getattr(self, attr)
            setattr(self, attr, pygame.transform.scale(img, (60, 60)))
            self.bullet_img = pygame.transform.scale(self.bullet_img, (15, 15))

        # inicjalizacja gracza
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), self.genesis_img, self.bullet_img)
        self.player.hp = 10

        # grupy sprite'ów
        self.crosshair          = Crosshair(self.player)
        self.bullets            = pygame.sprite.Group()
        self.enemy_bullets      = pygame.sprite.Group()
        self.ally_bullets       = pygame.sprite.Group()
        self.allies             = pygame.sprite.Group()
        self.enemies            = pygame.sprite.Group()

        self.reinforcement_queue = list(self.REINFORCEMENT_TYPES)
        self._space_pressed = False
        self._b_pressed     = False
        self._c_pressed     = False
        self.frame_count    = 0

        self.captor_spawned  = False
        self.captor_spawn_at = random.randint(60, 300)

        self.portal_active   = False
        self.portal_timer = 0
        self.portal_rect = self.portal_img.get_rect(midtop=(
            SCREEN_WIDTH // 2,
            50
        ))

        self.genesis_migrate = False
        self.bg_color        = bg_color or (30, 30, 30)

        self.score = 0
        self._spawn_enemies()

    def _create_sprite(self, color, size=(30, 30)):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    def _spawn_enemies(self):
        # Shooterzy
        shooter_positions = [(SCREEN_WIDTH // 5 * i, 100) for i in range(1, 5)]
        for pos in shooter_positions:
            self.enemies.add(Shooter(
                pos,
                self.shooter_img,
                self.player,
                self.enemy_bullets
            ))

        # Helikoptery i Chaserzy
        helicopter_positions = [
            (SCREEN_WIDTH // (self.number + 1) * (i + 1), 40)
            for i in range(self.number)
        ]

        for i in range(self.number * 3):
            x = 50 + (i * 70) % (SCREEN_WIDTH - 100)
            y = 150 + (i // 10) * 60

            if i % 5 == 4 and helicopter_positions:
                # wróg-helikopter
                self.enemies.add(Helicopter(
                    helicopter_positions.pop(),
                    self.alien_helicopter_img,
                    self.player,
                    self.enemy_bullets
                ))
            else:
                # co trzeci Chaser to czołg, reszta – piechota
                if i % 3 == 0:
                    sprite, etype = self.enemy_tank_img, "tank"
                else:
                    sprite, etype = self.enemy_solider_img, "infantry"

                # <-- Tutaj kluczowa zmiana: przekazujemy self.enemy_bullets -->
                self.enemies.add(Chaser(
                    (x, y),
                    sprite,
                    self.player,
                    self.enemy_bullets,
                    enemy_type=etype
                ))

    def run(self):
        clock = pygame.time.Clock()

        while True:
            self.frame_count += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None

            keys = pygame.key.get_pressed()
            # strzały gracza
            if keys[pygame.K_SPACE] and not keys[pygame.K_b]:
                if not self._space_pressed:
                    b = self.player.shoot()
                    if b: self.bullets.add(b)
                self._space_pressed = True
            else:
                self._space_pressed = False

            # przywołanie sojusznika
            if keys[pygame.K_c] and not self._c_pressed and self.reinforcement_queue and len(self.allies) < 6:
                unit_type = self.reinforcement_queue.pop(0)
                spawn = (self.player.rect.centerx, self.player.rect.top - 30)
                if unit_type == "infantry":
                    sprite = self.ally_solider_img
                elif unit_type == "helicopter":
                    sprite = self.ally_helicopter_img
                elif unit_type == "tank":
                    sprite = self.ally_tank_img
                else:
                    sprite = None
                ally = AlliedUnit(spawn, unit_type, self.enemies, self.ally_bullets, sprite=sprite)
                self.allies.add(ally)
                self._c_pressed = True
            elif not keys[pygame.K_c]:
                self._c_pressed = False

            # pojawienie Captora
            if not self.captor_spawned and self.frame_count >= self.captor_spawn_at and self.allies:
                pos = (random.randint(100, SCREEN_WIDTH - 100), 40)
                cap_spr = self.captor_img
                self.enemies.add(Captor(pos, cap_spr, self.allies, self.enemy_bullets))
                self.captor_spawned = True

            # logika i kolizje
            result = self._update_logic()
            if result is None:
                return None
            if result[0] != self.number:
                return result

            self._draw()
            pygame.display.flip()
            clock.tick(60)

    def _update_logic(self):
        # aktualizacja wszystkich grup
        self.player.update()
        self.crosshair.update()
        self.bullets.update()
        self.enemy_bullets.update()
        self.ally_bullets.update()
        self.allies.update()
        self.enemies.update()

        # 1) pociski gracza i sojuszników vs wrogowie
        for group, pts in [(self.bullets, 10), (self.ally_bullets, 5)]:
            for b in list(group):
                hits = pygame.sprite.spritecollide(b, self.enemies, False)
                for enemy in hits:
                    # UFO
                    if isinstance(enemy, Captor):
                        enemy.take_damage()
                        if enemy.hp <= 0:
                            enemy.kill()
                            self.score += 50
                    # Strzelec
                    elif isinstance(enemy, Shooter):
                        enemy.kill()
                    # Chaser: rozróżnij tank vs infantry
                    elif isinstance(enemy, Chaser):
                        if enemy.enemy_type == "tank":
                            enemy.hp -= 1
                            if enemy.hp <= 0:
                                enemy.kill()
                                self.score += pts * 2  # więcej za czołg
                        else:
                            enemy.kill()
                            self.score += pts
                    else:
                        enemy.kill()
                        self.score += pts
                    b.kill()

        # 2) wrogie pociski vs gracz
        for eb in list(self.enemy_bullets):
            if pygame.sprite.collide_rect(eb, self.player):
                eb.kill()
                self.player.hp -= 1
                if self.player.hp <= 0:
                    return None

        # 3) bezpośredni kontakt gracz–wróg
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            return None

        # 4) portal i zakończenie poziomu
        if not self.portal_active:
            if not any(isinstance(e, Shooter) for e in self.enemies):
                self.portal_active = True

        if self.portal_active and self.player.rect.colliderect(self.portal_rect):
            self.genesis_migrate = True

        if self.genesis_migrate:
            self.portal_timer += 1
            if self.portal_timer > 120:
                self.score_manager.save_score(self.score)
                next_bg = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                return self.number + 1, next_bg

        return self.number, self.bg_color

    def _draw(self):
        bg = self.field_imgs.get(self.number)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(self.bg_color)
        self.player.draw(self.screen)
        self.crosshair.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)
        self.ally_bullets.draw(self.screen)
        self.allies.draw(self.screen)
        self.enemies.draw(self.screen)

        if self.portal_active:
            self.screen.blit(self.portal_img, self.portal_rect)
            font = pygame.font.SysFont("Arial", 24)
            self.screen.blit(font.render(f"Wynik: {self.score}", True, (255,255,255)), (10,10))
            self.screen.blit(font.render(f"Sojusznicy: {len(self.allies)}", True, (0,255,0)), (10,40))
            self.screen.blit(font.render(f"Życia: {self.player.hp}", True, (255,0,0)), (10,70))
