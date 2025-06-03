import pygame                     # importujemy bibliotekę pygame do tworzenia gier
import random                     # importujemy moduł random do losowania wartości
from src.game.unit import Unit    # importujemy klasę bazową Unit
from src.game.bullet import Bullet  # importujemy klasę Bullet reprezentującą pocisk


class AlliedUnit(Unit):           # definiujemy klasę sojuszniczej jednostki dziedziczącą po Unit
    """
    Klasa sojuszników gracza (przechwyconych lub przywołanych)
    Typy jednostek: infantry, tank, artillery, helicopter
    """

    TYPE_STATS = {                # słownik przechowujący statystyki dla różnych typów
        "infantry": {             # statystyki dla piechoty
            "color": (0, 0, 255),        # kolor jednostki w formacie RGB (niebieski)
            "shoot_interval": 120,      # co ile klatek jednostka może oddać strzał
            "bullet_speed": 5,          # prędkość pocisku
            "size": (20, 20)            # szerokość i wysokość sprite'a jednostki
        },
        "tank": {                 # statystyki dla czołgu
            "color": (128, 128, 0),      # kolor oliwkowy
            "shoot_interval": 90,       # częstotliwość strzałów co 90 klatek
            "bullet_speed": 4,          # prędkość pocisku
            "size": (26, 26)            # rozmiar sprite'a czołgu
        },
        "artillery": {            # statystyki dla artylerii
            "color": (255, 255, 0),      # kolor żółty
            "shoot_interval": 150,      # co 150 klatek strzał
            "bullet_speed": 7,          # prędkość pocisku
            "size": (24, 24)            # rozmiar sprite'a artylerii
        },
        "helicopter": {           # statystyki dla helikoptera
            "color": (0, 255, 255),      # kolor cyjan
            "shoot_interval": 60,       # co 60 klatek strzał
            "bullet_speed": 6,          # prędkość pocisku
            "size": (20, 20)            # rozmiar sprite'a helikoptera
        },
    }

    def __init__(self, position, unit_type, target_group, bullet_group):
        # pobieramy statystyki dla danego typu jednostki lub domyślnie dla infantry
        stats = self.TYPE_STATS.get(unit_type, self.TYPE_STATS["infantry"])
        # tworzymy powierzchnię (sprite) o rozmiarze określonym w stats
        sprite = pygame.Surface(stats["size"], pygame.SRCALPHA)
        # rysujemy prostokąt w kolorze określonym w stats
        pygame.draw.rect(sprite, stats["color"], sprite.get_rect())
        # wywołujemy konstruktor klasy bazowej Unit, przekazując pozycję i gotowy sprite
        super().__init__(position, sprite)

        # zapisujemy typ jednostki
        self.type = unit_type
        # grupa obiektów, do których będziemy strzelać (np. wrogowie)
        self.target_group = target_group
        # grupa, do której dodajemy wystrzelone pociski
        self.bullet_group = bullet_group
        # licznik klatek od ostatniego strzału
        self.shoot_timer = 0
        # interwał (w klatkach) między kolejnymi strzałami
        self.shoot_interval = stats["shoot_interval"]
        # prędkość wystrzeliwanych pocisków
        self.bullet_speed = stats["bullet_speed"]

    def update(self):
        # zwiększamy licznik klatek
        self.shoot_timer += 1

        # jeśli licznik osiągnął interwał i są cele do strzelania
        if self.shoot_timer >= self.shoot_interval and self.target_group:
            # resetujemy licznik
            self.shoot_timer = 0
            # wybieramy losowo jeden cel z grupy wrogów
            target = random.choice(self.target_group.sprites())

            # obliczamy wektor od naszej jednostki do środka celu
            vec = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
            if vec.length() > 0:              # jeśli odległość jest większa niż zero
                direction = vec.normalize()   # normalizujemy wektor (jeden piksel = długość 1)
                # tworzymy nowy pocisk: pozycja startowa, wygląd i prędkość (wektor kierunku * speed)
                bullet = Bullet(
                    self.rect.center,
                    self._make_bullet_sprite(),
                    direction * self.bullet_speed
                )
                # dodajemy pocisk do grupy pocisków
                self.bullet_group.add(bullet)

        # wywołujemy metodę update z klasy bazowej (np. do ruchu, kolizji itp.)
        super().update()

    def _make_bullet_sprite(self):
        # tworzymy niewielką powierzchnię pod pocisk (6x6 pikseli, z kanałem alfa)
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        # dobieramy kolor pocisku taki sam jak kolor jednostki
        color = self.TYPE_STATS[self.type]["color"]
        # rysujemy na powierzchni kółko o promieniu 3 pikseli
        pygame.draw.circle(surf, color, (3, 3), 3)
        return surf  # zwracamy gotowy sprite pocisku
