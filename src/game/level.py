import pygame
import random
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from .bullet import PlayerBullet
from .player import Player
from .enemy import Shooter, Chaser, Captor, Helicopter
from .crosshair import Crosshair
from .allied_unit import AlliedUnit
from .explosion import Explosion
from .audio_manager import get_audio_manager


class ImageLoader:
    """Klasa pomocnicza do ładowania obrazów"""

    def __init__(self):
        self.image_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'image')

    def load(self, filename, size=None):
        try:
            img = pygame.image.load(os.path.join(self.image_dir, filename)).convert_alpha()
            return pygame.transform.scale(img, size) if size else img
        except pygame.error:
            # Fallback - tworzy kolorowy placeholder
            surf = pygame.Surface(size or (60, 60), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 255, 0), surf.get_rect())
            return surf


class Level:
    """Główna klasa poziomu gry"""

    def __init__(self, screen, number, score_manager):
        # Podstawowa konfiguracja
        self.screen = screen
        self.number = number
        self.score_manager = score_manager
        self.score = 0
        self.frame_count = 0

        # Stan gry
        self.portal_active = False
        self.portal_timer = 0
        self.levelup_played = False
        self._space_pressed = False
        self._c_pressed = False
        self.captor_spawned = False
        self.captor_spawn_at = random.randint(60, 300)

        # Inicjalizacja audio
        self.audio = get_audio_manager()
        self._setup_audio()

        # Ładowanie zasobów
        self.images = self._load_game_resources()

        self.bg_img = self.images['background']
        self.bullet_img = self.images['bullet']
        self.enemy_bullet_img = self.images['enemy_bullet']
        self.portal_img = self.images['portal']
        self.portal_rect = self.portal_img.get_rect(center=(SCREEN_WIDTH // 2, 60))

        # HUD
        self.score_img = self.images['score']
        self.allies_img = self.images['allies']
        self.heart_img = self.images['heart']

        # Enemy sprites
        self.shooter_img = self.images['shooter']
        self.enemy_soldier_img = self.images['enemy_soldier']
        self.enemy_tank_img = self.images['enemy_tank']
        self.enemy_helicopter_img = self.images['enemy_helicopter']
        self.captor_img = self.images['captor']

        # Ally sprites
        self.ally_soldier_img = self.images['ally_soldier']
        self.ally_tank_img = self.images['ally_tank']
        self.ally_helicopter_img = self.images['ally_helicopter']
        self.ally_bullet_img = self.images['bullet']  # lub self.images['bullet'] jeśli to jest właściwy

        # Inicjalizacja grup sprite'ów
        self.groups = self._create_sprite_groups()
        # Mapowanie grup na osobne atrybuty
        self.bullets = self.groups['bullets']
        self.enemy_bullets = self.groups['enemy_bullets']
        self.ally_bullets = self.groups['ally_bullets']
        self.enemies = self.groups['enemies']
        self.allies = self.groups['allies']
        self.explosions = self.groups['explosions']

        # Tworzenie jednostek
        self.player = self._create_player()
        self.crosshair = self._create_crosshair()
        self._spawn_enemies()

    def _setup_audio(self):
        """Konfiguracja systemu audio"""
        sounds_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'sounds')
        self.audio.load_all_game_sounds(sounds_dir)
        self.audio.play_background_music('background_audio')

    def _load_game_resources(self):
        """Ładowanie wszystkich zasobów graficznych"""
        loader = ImageLoader()
        images = {
            'player': loader.load('genesis.png', (60, 60)),
            'bullet': loader.load('ally_bullet.png', (15, 15)),
            'enemy_bullet': loader.load('bullet.png', (15, 15)),
            'portal': loader.load('portal.png', (80, 80)),
            'explosion': loader.load('explosion.png', (32, 32)),
            # HUD
            'score': loader.load('score.png', (28, 28)),
            'allies': loader.load('allies.png', (28, 28)),
            'heart': loader.load('heart.png', (28, 28)),
            # Przeciwnicy
            'shooter': loader.load('shooter.png', (60, 60)),
            'enemy_soldier': loader.load('enemy_soldier.png', (60, 60)),
            'enemy_tank': loader.load('enemy_tank.png', (60, 60)),
            'enemy_helicopter': loader.load('enemy_helicopter.png', (60, 60)),
            'captor': loader.load('captor.png', (60, 60)),
            # Sojusznicy
            'ally_soldier': loader.load('ally_soldier.png', (60, 60)),
            'ally_tank': loader.load('ally_tank.png', (60, 60)),
            'ally_helicopter': loader.load('ally_helicopter.png', (60, 60))
        }

        # Tło poziomu
        bg_file = f'field_{self.number}.png'
        images['background'] = loader.load(bg_file, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Konfiguracja eksplozji
        Explosion.images = [images['explosion'],
                            pygame.transform.flip(images['explosion'], 1, 1)]

        return images

    def _create_sprite_groups(self):
        """Tworzenie wszystkich grup sprite'ów"""
        return {
            'bullets': pygame.sprite.Group(),
            'enemy_bullets': pygame.sprite.Group(),
            'ally_bullets': pygame.sprite.Group(),
            'enemies': pygame.sprite.Group(),
            'allies': pygame.sprite.Group(),
            'explosions': pygame.sprite.Group()
        }

    def _create_player(self):
        """Tworzenie gracza"""
        player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
                        self.images['player'],
                        self.images['bullet'])
        player.hp = 10
        return player

    def _create_crosshair(self):
        """Tworzenie celownika"""
        crosshair = Crosshair((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250))
        crosshair.player = self.player
        self.player.crosshair = crosshair
        return crosshair

    def _spawn_enemies(self):
        # Shooterzy
        shooter_positions = [(SCREEN_WIDTH // 5 * i, 100) for i in range(1, 5)]
        for pos in shooter_positions:
            self.enemies.add(Shooter(
                pos,
                self.shooter_img,
                self.player,
                self.enemy_bullets,
                bullet_sprite=self.enemy_bullet_img  # ZMIENIONE
            ))

        # Helikoptery i Chaserzy - używaj enemy_ grafik
        helicopter_positions = [
            (SCREEN_WIDTH // (self.number + 1) * (i + 1), 40)
            for i in range(self.number)
        ]

        for i in range(self.number * 3):
            x = 50 + (i * 70) % (SCREEN_WIDTH - 100)
            y = 150 + (i // 10) * 60

            if i % 5 == 4 and helicopter_positions:
                # Enemy Helikopter
                self.enemies.add(Helicopter(
                    helicopter_positions.pop(),
                    self.enemy_helicopter_img,
                    self.player,
                    self.enemy_bullets,
                    bullet_sprite=self.enemy_bullet_img
                ))
            else:
                # Enemy Chaser
                if i % 3 == 0:
                    sprite, etype = self.enemy_tank_img, "tank"
                else:
                    sprite, etype = self.enemy_soldier_img, "infantry"

                self.enemies.add(Chaser(
            (x, y),
                    sprite,
                    self.player,
                    self.enemy_bullets,
                    enemy_type=etype,
                    bullet_sprite=self.enemy_bullet_img
                ))

    def _draw_hud(self):
        """Rysowanie HUD z ikonami"""
        font = pygame.font.SysFont("Arial", 24)

        hud_y = 10
        text_offset = 32

        # Wynik
        score_x = 10
        self.screen.blit(self.score_img, (score_x, hud_y))
        score_text = font.render(f"{self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (score_x + text_offset, hud_y + 2))

        # Sojusznicy
        allies_x = 150
        self.screen.blit(self.allies_img, (allies_x, hud_y))
        allies_text = font.render(f"{len(self.allies)}", True, (0, 255, 0))
        self.screen.blit(allies_text, (allies_x + text_offset, hud_y + 2))

        # Życia
        lives_x = 280
        self.screen.blit(self.heart_img, (lives_x, hud_y))
        lives_text = font.render(f"{self.player.hp}", True, (255, 0, 0))
        self.screen.blit(lives_text, (lives_x + text_offset, hud_y + 2))

    def _draw_portal(self):
        """Rysuje portal z efektem pulsowania"""
        if self.portal_active:
            pulse = abs(pygame.time.get_ticks() % 2000 - 1000) / 1000.0
            alpha = int(128 + 127 * pulse)

            portal_surface = self.portal_img.copy()
            portal_surface.set_alpha(alpha)
            self.screen.blit(portal_surface, self.portal_rect)

    def _draw(self):
        self.screen.blit(self.bg_img, (0, 0))

        self.player.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)
        self.ally_bullets.draw(self.screen)
        self.allies.draw(self.screen)
        self.enemies.draw(self.screen)
        self.explosions.draw(self.screen)
        self.crosshair.draw(self.screen)

        self._draw_portal()
        self._draw_hud()


        pygame.display.flip()

    def _update_logic(self):
        # Aktualizacja wszystkich grup
        self.player.update()
        self.crosshair.update()
        self.bullets.update()
        self.enemy_bullets.update()
        self.ally_bullets.update()
        self.allies.update()
        self.enemies.update()
        self.explosions.update()

        #
        for captor in [e for e in self.enemies if isinstance(e, Captor)]:
            hit_allies = pygame.sprite.spritecollide(captor, self.allies, dokill=True)
            if hit_allies:
                self.audio.play_sound('capture_audio')  # jeśli masz taki plik
                explosion = Explosion(captor.rect.center)
                self.explosions.add(explosion)

        # 1) pociski gracza i sojuszników vs wrogowie
        for group, pts in [(self.bullets, 10), (self.ally_bullets, 5)]:
            for b in list(group):
                hits = pygame.sprite.spritecollide(b, self.enemies, False)
                for enemy in hits:
                    # Tworzymy eksplozję w miejscu trafienia
                    explosion = Explosion(enemy.rect.center)
                    self.explosions.add(explosion)

                    # UFO
                    if isinstance(enemy, Captor):
                        enemy.take_damage()
                        if enemy.hp <= 0:
                            enemy.kill()
                            self.score += 50
                    # Strzelec
                    elif isinstance(enemy, Shooter):
                        enemy.kill()
                        self.score += pts
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

                    # Dźwięk eksplozji
                    self.audio.play_sound('explosion_audio')

        # 2) wrogie pociski vs gracz
        for eb in list(self.enemy_bullets):
            if pygame.sprite.collide_rect(eb, self.player):
                explosion = Explosion(eb.rect.center)
                self.explosions.add(explosion)
                eb.kill()
                self.player.hp -= 1
                if self.player.hp <= 0:
                    # Zatrzymaj muzykę w tle
                    self.audio.stop_background_music()
                    # Odtwórz dźwięk śmierci gracza
                    self.audio.play_sound('player_die')
                    # Po krótkiej przerwie odtwórz game over
                    pygame.time.wait(1000)
                    self.audio.play_sound('game_over_audio')
                    return "game_over"

        # 3) bezpośredni kontakt gracz–wróg
        if any(pygame.sprite.collide_mask(self.player, e) for e in self.enemies):
            explosion = Explosion(self.player.rect.center)
            self.explosions.add(explosion)
            self.audio.stop_background_music()
            self.audio.play_sound('player_die')
            pygame.time.wait(1000)
            self.audio.play_sound('game_over_audio')
            return "game_over"

        # 4) portal i zakończenie poziomu
        if not self.portal_active:
            shooters_left = [e for e in self.enemies if isinstance(e, Shooter)]
            if len(shooters_left) == 0 and not self.levelup_played:
                # Dźwięk level up gdy zostaje ostatni shooter
                self.audio.play_sound('levelup_audio')
                self.levelup_played = True

            if not any(isinstance(e, Shooter) for e in self.enemies):
                self.portal_active = True

        if self.portal_active and self.player.rect.colliderect(self.portal_rect):
            self.portal_timer += 1
            if self.portal_timer > 120:
                # Dodaj punkty do score_manager
                self.score_manager.add_score(self.score)

                # Zatrzymaj wszystkie dźwięki
                self.audio.stop_background_music()

                # Zwróć string zamiast tuple
                return "next_level"

        return "continue"

    def run(self,unit_count):
        clock = pygame.time.Clock()

        while True:
            self.frame_count += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None

            keys = pygame.key.get_pressed()
            self.crosshair.update()

            # strzały gracza
            if keys[pygame.K_SPACE]:
                if not self._space_pressed:
                    b = PlayerBullet(
                        self.player.rect.center,
                        self.bullet_img,  # POPRAWIONY ROZMIAR
                        pygame.math.Vector2(0, -10),
                        self.crosshair,
                        self.explosions
                    )
                    if b:
                        self.bullets.add(b)
                        # Dźwięk strzału gracza
                        self.audio.play_sound('shoot_effect')
                self._space_pressed = True
            else:
                self._space_pressed = False

            # POPRAWIONE PRZYWOŁYWANIE SOJUSZNIKÓW
            if keys[pygame.K_c] and not self._c_pressed and len(self.allies) < unit_count:
                unit_types = ["infantry", "tank", "helicopter"]
                unit_type = random.choice(unit_types)
                spawn = (self.player.rect.centerx, self.player.rect.top - 30)

                # POPRAWIONE MAPOWANIE SPRITE'ÓW
                if unit_type == "infantry":
                    sprite = self.ally_soldier_img
                elif unit_type == "helicopter":
                    sprite = self.ally_helicopter_img
                elif unit_type == "tank":
                    sprite = self.ally_tank_img
                else:
                    sprite = self.ally_soldier_img

                ally = AlliedUnit(
                    spawn,
                    unit_type,
                    self.enemies,
                    self.ally_bullets,
                    bullet_sprite=self.ally_bullet_img,  # SOJUSZNICY UŻYWAJĄ ally_bullet
                    sprite=sprite
                )
                self.allies.add(ally)
                self._c_pressed = True
            elif not keys[pygame.K_c]:
                self._c_pressed = False

            # pojawienie Captora
            if not self.captor_spawned and self.frame_count >= self.captor_spawn_at and self.allies:
                pos = (random.randint(100, SCREEN_WIDTH - 100), 40)
                self.enemies.add(Captor(
                    pos,
                    self.captor_img,
                    self.allies,
                    self.enemy_bullets,
                    bullet_sprite=self.enemy_bullet_img
                ))
                self.captor_spawned = True

            # logika i kolizje
            result = self._update_logic()
            if result is None:
                return None
            if result == "next_level":
                return "next_level"
            if result == "game_over":
                return "game_over"

            self._draw()
            clock.tick(60)