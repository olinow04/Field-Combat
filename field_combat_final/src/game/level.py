import pygame                                        # importujemy pygame do obsługi grafiki i zdarzeń
import random                                        # importujemy moduł random do losowania wartości

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT   # pobieramy stałe szerokości i wysokości ekranu
from .player import Player                           # importujemy klasę gracza
from .enemy import Shooter, Chaser, Captor, Helicopter  # importujemy różne typy wrogów
from .crosshair import Crosshair                     # importujemy klasę celownika
from .beam import Beam                               # importujemy klasę promienia przechwytującego
from .allied_unit import AlliedUnit                  # importujemy klasę jednostki sojuszniczej

PORTAL_WIDTH = 60                                   # szerokość portalu w pikselach
PORTAL_HEIGHT = 40                                  # wysokość portalu w pikselach
PORTAL_COLOR = (255, 0, 255)                        # kolor portalu (fioletowy)
PORTAL_Y = 10                                       # pozycja Y portalu na samej górze ekranu

class Level:                                        # definiujemy klasę obsługującą poziom gry
    """
    Klasa zarządzająca logiką poziomu gry Field Combat.
    Odpowiada za inicjalizację obiektów, główną pętlę, kolizje, respawn i renderowanie.
    """

    REINFORCEMENT_TYPES = [                         # kolejka rodzajów posiłków do przywołania
        "infantry", "tank", "artillery",
        "helicopter", "infantry", "tank"
    ]

    def __init__(self, screen, number, score_manager, bg_color=None):
        self.screen = screen                         # powierzchnia, na której rysujemy grę
        self.number = number                         # numer bieżącego poziomu
        self.score_manager = score_manager           # obiekt do zarządzania wynikami

        # Inicjalizacja gracza (Genesis)
        self.player = Player(
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),  # startowa pozycja w połowie szerokości, u dołu
            self._create_sprite((0, 255, 0))            # tworzymy zielony sprite gracza
        )
        self.player.hp = 10                           # ustawiamy punkty życia gracza

        # Celownik nad graczem
        self.crosshair = Crosshair(self.player)       # tworzymy obiekt celownika powiązany z graczem

        # Grupy sprite'ów (do aktualizacji i rysowania)
        self.bullets = pygame.sprite.Group()          # pociski gracza
        self.enemy_bullets = pygame.sprite.Group()    # pociski wrogów
        self.ally_bullets = pygame.sprite.Group()     # pociski sojuszników
        self.beams = pygame.sprite.Group()            # promienie przechwytujące
        self.allies = pygame.sprite.Group()           # sojusznicy przywołani
        self.enemies = pygame.sprite.Group()          # wrogowie

        # Kolejka posiłków do przywołania
        self.reinforcement_queue = list(self.REINFORCEMENT_TYPES)

        # Flagi blokujące wielokrotne wciśnięcie klawiszy
        self._space_pressed = False                   # flaga strzału główną bronią
        self._b_pressed = False                       # flaga promienia
        self._c_pressed = False                       # flaga przywołania sojuszników

        # Mechanika Captora (UFO porywającego sojuszników)
        self.frame_count = 0                          # licznik klatek od startu poziomu
        self.captor_spawned = False                   # czy UFO już się pojawiło
        self.captor_spawn_at = random.randint(60, 300)  # losowy czas pojawienia się UFO (1–5 sek.)

        # Portal do kolejnego poziomu
        self.portal_active = False                    # flaga aktywacji portalu
        self.portal_rect = pygame.Rect(               # prostokąt portalu w środku ekranu
            SCREEN_WIDTH // 2 - PORTAL_WIDTH // 2,
            PORTAL_Y,
            PORTAL_WIDTH,
            PORTAL_HEIGHT
        )
        self.portal_timer = 0                         # licznik migania gracza w portalu
        self.genesis_migrate = False                  # flaga rozpoczęcia migracji gracza do portalu

        # Kolor tła ekranu (opcjonalny lub losowany)
        if bg_color is None:
            self.bg_color = (30, 30, 30)              # domyślny ciemnoszary kolor tła
        else:
            self.bg_color = bg_color                  # kolor podany w argumencie

        # Generujemy początkowe fale wrogów
        self._spawn_enemies()
        self.score = 0                                # bieżący wynik gracza

    def _create_sprite(self, color, size=(30, 30)):
        surf = pygame.Surface(size, pygame.SRCALPHA)   # tworzymy przezroczystą powierzchnię o zadanym rozmiarze
        surf.fill(color)                               # wypełniamy ją kolorem
        return surf                                    # zwracamy gotowy sprite

    def _spawn_enemies(self):
        # Stała liczba 4 Shooterów w linii poziomej
        shooter_positions = [
            (SCREEN_WIDTH // 5 * 1, 100),
            (SCREEN_WIDTH // 5 * 2, 100),
            (SCREEN_WIDTH // 5 * 3, 100),
            (SCREEN_WIDTH // 5 * 4, 100)
        ]

        # Tworzenie 4 Shooterów
        for pos in shooter_positions:
            self.enemies.add(Shooter(
                pos,
                self._create_sprite((255, 0, 0)),
                self.player,
                self.enemy_bullets
            ))

        # Reszta wrogów zależna od poziomu
        helicopter_positions = []
        num_helicopters = self.number
        spacing = SCREEN_WIDTH // (num_helicopters + 1)

        for h in range(num_helicopters):
            x = spacing * (h + 1)
            helicopter_positions.append((x, 40))

        # Tworzenie Chaserów i Helicopterów
        for i in range(self.number * 3):  # Zmniejszono mnożnik z 5 do 3
            x = 50 + (i * 70) % (SCREEN_WIDTH - 100)
            y = 150 + (i // 10) * 60  # Zwiększono Y by uniknąć nakładania

            if i % 5 == 4 and len(helicopter_positions) > 0:
                self.enemies.add(Helicopter(
                    helicopter_positions.pop(),
                    self._create_sprite((0, 255, 255)),
                    self.player,
                    self.enemy_bullets
                ))
            else:
                self.enemies.add(Chaser(
                    (x, y),
                    self._create_sprite((255, 0, 0)),
                    self.player,
                    self.bullets  # <-- dodaj tę grupę
                ))

    def run(self):
        clock = pygame.time.Clock()                    # zegar do utrzymania stałego FPS
        next_bg_color = self.bg_color                  # kolor tła na kolejny poziom
        while True:
            self.frame_count += 1                      # zwiększamy licznik klatek

            # Obsługa zdarzeń okna (zamknięcie gry)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None

            keys = pygame.key.get_pressed()            # pobieramy stan wszystkich klawiszy

            # Strzał główną bronią (klawisz SPACE)
            if keys[pygame.K_SPACE] and not keys[pygame.K_b]:
                if not self._space_pressed:
                    b = self.player.shoot()           # gracz strzela
                    if b:
                        self.bullets.add(b)           # dodajemy pocisk do grupy
                    self._space_pressed = True
            else:
                self._space_pressed = False

            # Promień przechwytujący (klawisz B)
            if keys[pygame.K_b] and not keys[pygame.K_SPACE]:
                if not self._b_pressed:
                    beam = Beam(self.player.rect.center, self.crosshair.rect.center)
                    self.beams.add(beam)              # dodajemy promień
                    self._b_pressed = True
            else:
                self._b_pressed = False

            # Przywoływanie sojuszników (klawisz C)
            if keys[pygame.K_c]:
                if not self._c_pressed and self.reinforcement_queue and len(self.allies) < 6:
                    unit_type = self.reinforcement_queue.pop(0)  # wyciągamy typ z kolejki
                    spawn_pos = (self.player.rect.centerx, self.player.rect.top - 30)
                    ally = AlliedUnit(spawn_pos, unit_type, self.enemies, self.ally_bullets)
                    self.allies.add(ally)            # dodajemy jednostkę do grupy sojuszników
                    self._c_pressed = True
            else:
                self._c_pressed = False

            # Pojawienie się Captora (UFO) jeśli są sojusznicy i minął czas
            if not self.captor_spawned and self.frame_count >= self.captor_spawn_at and len(self.allies) > 0:
                pos = (random.randint(100, SCREEN_WIDTH - 100), 40)
                cap_spr = self._create_sprite((255, 255, 0), (30, 30))  # żółty sprite UFO
                self.enemies.add(
                    Captor(pos, cap_spr, self.allies, self.enemy_bullets)
                )
                self.captor_spawned = True

            # Aktualizacja logiki gry (ruch, kolizje itp.)
            next_level, next_bg_color = self._update_logic()
            if next_level is None:
                return None                           # koniec gry
            elif next_level != self.number:
                return next_level, next_bg_color      # przejście do nowego poziomu

            # Renderowanie sceny
            self._draw()
            pygame.display.flip()                    # aktualizujemy ekran
            clock.tick(60)                           # limitujemy do 60 FPS

    def _update_logic(self):
        # wywołujemy update dla wszystkich obiektów
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
        self.screen.fill(self.bg_color)  # tło

        self.player.draw(self.screen)
        self.crosshair.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)
        self.ally_bullets.draw(self.screen)
        self.beams.draw(self.screen)
        self.allies.draw(self.screen)
        self.enemies.draw(self.screen)

        # Rysujemy ramkę portalu, jeśli jest aktywny
        if self.portal_active:
            pygame.draw.rect(self.screen, PORTAL_COLOR, self.portal_rect, 3)

        # --- WYŚWIETLANIE PUNKTACJI W CZASIE RZECZYWISTYM ---
        font = pygame.font.SysFont("Arial", 24)
        score_surf = font.render(f"Wynik: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))

        # (opcjonalnie) liczba sojuszników i życia gracza
        allies_surf = font.render(f"Sojusznicy: {len(self.allies)}", True, (0, 255, 0))
        lives_surf = font.render(f"Życia: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(allies_surf, (10, 40))
        self.screen.blit(lives_surf, (10, 70))
