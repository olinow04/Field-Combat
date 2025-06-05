# game/unit.py

import pygame                                  # importujemy pygame do obsługi grafiki i sprite'ów

class Unit(pygame.sprite.Sprite):              # definiujemy bazową klasę jednostki dziedziczącą po Sprite
    """
    Bazowa klasa dla wszystkich jednostek w grze
    Zawiera podstawową logikę ruchu i renderowania
    """

    def __init__(self, position, sprite):
        super().__init__()                      # wywołujemy konstruktor rodzica, dodajemy się do systemu sprite'ów
        self.image = sprite                     # ustawiamy grafikę jednostki (surface)
        # tworzymy prostokąt do pozycjonowania i kolizji, ze środkiem w podanym punkcie
        self.rect = self.image.get_rect(center=position)
        # wektor prędkości jednostki; na start zerowy (brak ruchu)
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        # przesuwamy prostokąt jednostki o wektor velocity
        self.rect.move_ip(self.velocity)

    def draw(self, surface):
        # rysujemy grafikę jednostki na przekazanej powierzchni (screen albo inny surface)
        surface.blit(self.image, self.rect)
