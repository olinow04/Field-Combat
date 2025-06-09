# game/bullet.py

import pygame                                       # importujemy bibliotekę pygame do obsługi grafiki i wektorów
from src.game.unit import Unit                      # importujemy klasę bazową Unit, z której dziedziczy Bullet

class Bullet(Unit):                                 # definiujemy klasę Bullet dziedziczącą po Unit
    def __init__(self, position, sprite, velocity): # konstruktor przyjmuje pozycję startową, grafikę i wektor prędkości
        super().__init__(position, sprite)          # wywołujemy konstruktor Unit, ustawiając pozycję i obrazek
        self.velocity = pygame.math.Vector2(velocity)  # zamieniamy przekazaną prędkość na obiekt Vector2

    def update(self):                               # metoda update wywoływana co klatkę
        # przesuwamy pocisk o wektor velocity
        self.rect.move_ip(self.velocity)

        # sprawdzamy, czy pocisk wciąż jest na ekranie
        screen_rect = pygame.display.get_surface().get_rect()  # pobieramy prostokąt ekranu
        if not screen_rect.colliderect(self.rect):  # jeśli prostokąt pocisku i ekranu się nie pokrywają
            self.kill()                             # usuwamy pocisk z gry (ze wszystkich grup)
