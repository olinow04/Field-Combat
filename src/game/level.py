import pygame
import random
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from .bullet import PlayerBullet
from .player import Player
from .enemy import Shooter, Chaser, Captor, Helicopter
from .crosshair import Crosshair
from .allied_unit import AlliedUnit
from src.game.explosion import Explosion
from .audio_manager import get_audio_manager


class Level:
    def __init__(self, screen, number, score_manager):
        self.screen = screen
        self.number = number
        self.score_manager = score_manager

        # Inicjalizacja audio managera
        self.audio = get_audio_manager()

        # Ładowanie dźwięków
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        sounds_dir = os.path.join(project_root, 'sounds')
        self.audio.load_all_game_sounds(sounds_dir)

        # Rozpocznij muzykę w tle
        self.audio.play_background_music('background_audio')

        # Flagi dla dźwięków
        self.levelup_played = False
        self.player_death_started = False
        self.game_over_timer = 0

        # Wczytywanie obrazków
        image_dir = os.path.join(project_root, 'image')

        # Gracz (genesis.png)
        try:
            self.genesis_img = pygame.image.load(os.path.join(image_dir, 'genesis.png')).convert_alpha()
            self.genesis_img = pygame.transform.scale(self.genesis_img, (60, 60))
        except pygame.error:
            self.genesis_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.genesis_img, (0, 255, 0), (0, 0, 60, 60))

        # Pociski - GRACZ I SOJUSZNICY UŻYWAJĄ ally_bullet.png
        try:
            # Pocisk sojuszników i gracza (ally_bullet.png)
            self.ally_bullet_img = pygame.image.load(os.path.join(image_dir, 'ally_bullet.png')).convert_alpha()
            self.ally_bullet_img = pygame.transform.scale(self.ally_bullet_img, (15, 15))

            # Pocisk gracza - taki sam jak sojuszników
            self.bullet_img = self.ally_bullet_img

            # Pocisk wrogów (bullet.png)
            self.enemy_bullet_img = pygame.image.load(os.path.join(image_dir, 'bullet.png')).convert_alpha()
            self.enemy_bullet_img = pygame.transform.scale(self.enemy_bullet_img, (15, 15))
        except pygame.error:
            self.ally_bullet_img = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.ally_bullet_img, (0, 255, 0), (7, 7), 7)
            self.bullet_img = self.ally_bullet_img
            self.enemy_bullet_img = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.enemy_bullet_img, (255, 0, 0), (7, 7), 7)

        # WROGOWIE - używaj enemy_ grafik
        try:
            self.shooter_img = pygame.image.load(os.path.join(image_dir, 'shooter.png')).convert_alpha()
            self.shooter_img = pygame.transform.scale(self.shooter_img, (60, 60))
        except pygame.error:
            self.shooter_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.shooter_img, (0, 255, 255), (0, 0, 60, 60))

        try:
            self.enemy_soldier_img = pygame.image.load(os.path.join(image_dir, 'enemy_soldier.png')).convert_alpha()
            self.enemy_soldier_img = pygame.transform.scale(self.enemy_soldier_img, (60, 60))
        except pygame.error:
            self.enemy_soldier_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.enemy_soldier_img, (255, 0, 0), (0, 0, 60, 60))

        try:
            self.enemy_tank_img = pygame.image.load(os.path.join(image_dir, 'enemy_tank.png')).convert_alpha()
            self.enemy_tank_img = pygame.transform.scale(self.enemy_tank_img, (60, 60))
        except pygame.error:
            self.enemy_tank_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.enemy_tank_img, (100, 100, 100), (0, 0, 60, 60))

        try:
            self.enemy_helicopter_img = pygame.image.load(
                os.path.join(image_dir, 'enemy_helicopter.png')).convert_alpha()
            self.enemy_helicopter_img = pygame.transform.scale(self.enemy_helicopter_img, (60, 60))
        except pygame.error:
            self.enemy_helicopter_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.enemy_helicopter_img, (0, 255, 0), (0, 0, 60, 60))

        try:
            self.captor_img = pygame.image.load(os.path.join(image_dir, 'captor.png')).convert_alpha()
            self.captor_img = pygame.transform.scale(self.captor_img, (60, 60))
        except pygame.error:
            self.captor_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(self.captor_img, (255, 0, 255), (30, 30), 30)

        # SOJUSZNICY - używaj ally_ grafik
        try:
            self.ally_soldier_img = pygame.image.load(os.path.join(image_dir, 'ally_soldier.png')).convert_alpha()
            self.ally_soldier_img = pygame.transform.scale(self.ally_soldier_img, (60, 60))
        except pygame.error:
            self.ally_soldier_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.ally_soldier_img, (0, 255, 0), (0, 0, 60, 60))

        try:
            self.ally_tank_img = pygame.image.load(os.path.join(image_dir, 'ally_tank.png')).convert_alpha()
            self.ally_tank_img = pygame.transform.scale(self.ally_tank_img, (60, 60))
        except pygame.error:
            self.ally_tank_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.ally_tank_img, (0, 100, 0), (0, 0, 60, 60))

        try:
            self.ally_helicopter_img = pygame.image.load(os.path.join(image_dir, 'ally_helicopter.png')).convert_alpha()
            self.ally_helicopter_img = pygame.transform.scale(self.ally_helicopter_img, (60, 60))
        except pygame.error:
            self.ally_helicopter_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.ally_helicopter_img, (0, 150, 0), (0, 0, 60, 60))

        # Pozostałe grafiki
        try:
            self.portal_img = pygame.image.load(os.path.join(image_dir, 'portal.png')).convert_alpha()
            self.portal_img = pygame.transform.scale(self.portal_img, (80, 80))
        except pygame.error:
            self.portal_img = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(self.portal_img, (255, 0, 255), (40, 40), 40)

        # HUD images
        try:
            self.score_img = pygame.image.load(os.path.join(image_dir, 'score.png')).convert_alpha()
            self.score_img = pygame.transform.scale(self.score_img, (28, 28))
        except pygame.error:
            self.score_img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.rect(self.score_img, (255, 255, 0), (0, 0, 28, 28))

        try:
            self.allies_img = pygame.image.load(os.path.join(image_dir, 'allies.png')).convert_alpha()
            self.allies_img = pygame.transform.scale(self.allies_img, (28, 28))
        except pygame.error:
            self.allies_img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.rect(self.allies_img, (0, 255, 0), (0, 0, 28, 28))

        try:
            self.heart_img = pygame.image.load(os.path.join(image_dir, 'heart.png')).convert_alpha()
            self.heart_img = pygame.transform.scale(self.heart_img, (28, 28))
        except pygame.error:
            self.heart_img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(self.heart_img, (255, 0, 0), (14, 14), 14)

        # Eksplozje
        try:
            self.explosion_img = pygame.image.load(os.path.join(image_dir, 'explosion.png')).convert_alpha()
            self.explosion_img = pygame.transform.scale(self.explosion_img, (32, 32))
            Explosion.images = [self.explosion_img, pygame.transform.flip(self.explosion_img, 1, 1)]
        except pygame.error:
            self.explosion_img = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.explosion_img, (255, 100, 0), (16, 16), 16)
            Explosion.images = [self.explosion_img]

        # TŁA - POPRAWIONE NAZWY PLIKÓW
        field_files = {
            1: 'field_1.png',
            2: 'field_2.png',
            3: 'field_3.png'
        }

        # DODAJ DEBUGGING:
        print(f"Loading level {self.number}")
        bg_file = field_files.get(self.number, 'field_1.png')
        print(f"Using background: {bg_file}")

        try:
            self.bg_img = pygame.image.load(os.path.join(image_dir, bg_file)).convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print(f"Successfully loaded {bg_file}")
        except pygame.error as e:
            print(f"Failed to load {bg_file}: {e}")
            self.bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_img.fill((50, 100, 50))

        # Inicjalizacja grup sprite'ów
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.ally_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.allies = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        # Tworzenie gracza
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), self.genesis_img, self.bullet_img)
        self.player.hp = 10

        # Crosshair
        self.crosshair = Crosshair((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250))
        self.crosshair.player = self.player
        self.player.crosshair = self.crosshair

        # Portal
        self.portal_active = False
        self.portal_timer = 0
        self.portal_rect = self.portal_img.get_rect(midtop=(SCREEN_WIDTH // 2, 50))

        # Spawn wrogów
        self._spawn_enemies()

        # Zmienne kontrolne
        self._space_pressed = False
        self._c_pressed = False
        self.frame_count = 0

        # Captor spawning
        self.captor_spawned = False
        self.captor_spawn_at = random.randint(60, 300)

        self.score = 0

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
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            explosion = Explosion(self.player.rect.center)
            self.explosions.add(explosion)
            # Zatrzymaj muzykę w tle
            self.audio.stop_background_music()
            # Odtwórz dźwięk śmierci gracza
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

    def run(self):
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
            if keys[pygame.K_c] and not self._c_pressed and len(self.allies) < 6:
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
                self.score_manager.add_score(-20)
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
