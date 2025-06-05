# game/crosshair.py

import pygame  # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń

class Crosshair(pygame.sprite.Sprite):  # definiujemy klasę celownika dziedziczącą po Sprite
    def __init__(self, player, offset=(0, -150), size=32, color=(255,255,0)):
        """
        :param player: obiekt gracza (Genesis)
        :param offset: wektor przesunięcia celownika względem pozycji gracza
        :param size: rozmiar kwadratu celownika w pikselach
        :param color: kolor linii i kółka celownika
        """
        super().__init__()  # wywołanie konstruktora klasy bazowej Sprite
        self.player = player  # przypisanie referencji do obiektu gracza
        self.offset = pygame.math.Vector2(offset)  # tworzymy wektor przesunięcia celownika
        self.size = size  # zapisujemy rozmiar kwadratu celownika
        self.color = color  # zapisujemy kolor linii celownika

        # tworzymy przezroczystą powierzchnię (surface) o rozmiarze size×size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # rysujemy ramkę kwadratu w podanym kolorze, szerokość linii = 1 piksel
        pygame.draw.rect(self.image, color, (0, 0, size, size), 1)
        # rysujemy poziomą linię na środku kwadratu
        pygame.draw.line(self.image, color, (0, size//2), (size, size//2), 1)
        # rysujemy pionową linię na środku kwadratu
        pygame.draw.line(self.image, color, (size//2, 0), (size//2, size), 1)
        # rysujemy kółko o promieniu 4 pikseli w środku kwadratu
        pygame.draw.circle(self.image, color, (size // 2, size // 2), 4)
        # pobieramy prostokąt (rect) do pozycjonowania sprite'a
        self.rect = self.image.get_rect()

    def update(self):
        # ustawiamy środek rect na pozycję gracza przesuniętą o offset
        self.rect.center = self.player.rect.center + self.offset

    def draw(self, surface):
        # rysujemy obraz celownika na podanej powierzchni (surface)
        surface.blit(self.image, self.rect)
