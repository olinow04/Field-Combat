import pygame                                        # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń
from src.game.unit import Unit                       # importujemy klasę bazową Unit (po niej dziedziczy Player)
from src.game.bullet import Bullet                   # importujemy klasę Bullet reprezentującą pocisk

class Player(Unit):                                  # definiujemy klasę gracza dziedziczącą po Unit
    SPEED = 4                                        # stała prędkość ruchu gracza (piksele na klatkę)

    def __init__(self, position, sprite):
        super().__init__(position, sprite)          # wywołujemy konstruktor Unit z pozycją i grafiką
        self.velocity = pygame.math.Vector2(0, 0)    # wektor prędkości, na początku zerowy
        self.hp = 3                                   # punkty życia gracza

    def handle_input(self):
        # obsługa klawiatury do ruchu gracza
        keys = pygame.key.get_pressed()              # pobieramy stan wszystkich klawiszy
        self.velocity = pygame.math.Vector2(0, 0)    # zerujemy wektor prędkości przed każdą aktualizacją

        # poruszanie w lewo i prawo
        if keys[pygame.K_LEFT]:
            self.velocity.x = -self.SPEED            # ruch w lewo zmniejsza współrzędną x
        if keys[pygame.K_RIGHT]:
            self.velocity.x = self.SPEED             # ruch w prawo zwiększa współrzędną x

        # poruszanie w górę i dół
        if keys[pygame.K_UP]:
            self.velocity.y = -self.SPEED            # ruch w górę zmniejsza współrzędną y
        if keys[pygame.K_DOWN]:
            self.velocity.y = self.SPEED             # ruch w dół zwiększa współrzędną y

    def shoot(self):
        # tworzenie pocisku wystrzelonego przez gracza
        bullet_sprite = pygame.Surface((5, 5))        # tworzymy mały kwadrat 5×5 pikseli
        bullet_sprite.fill((255, 0, 0))               # wypełniamy go kolorem czerwonym
        direction = pygame.math.Vector2(0, -10)       # definiujemy wektor ruchu pocisku w górę
        return Bullet(self.rect.center, bullet_sprite, direction)
                                                     # tworzymy obiekt Bullet i zwracamy go

    def update(self):
        self.handle_input()                           # najpierw obsługujemy wejście od gracza
        self.rect.move_ip(self.velocity)              # przesuwamy prostokąt gracza o wektor prędkości

        # ograniczenie gracza do obszaru ekranu
        screen_rect = pygame.display.get_surface().get_rect()
                                                     # pobieramy prostokąt aktualnego ekranu
        self.rect.clamp_ip(screen_rect)               # ograniczamy rect gracza do wnętrza ekranu
