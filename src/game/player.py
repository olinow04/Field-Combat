import pygame                                        # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń
from src.game.unit import Unit                       # importujemy klasę bazową Unit (po niej dziedziczy Player)
from src.game.bullet import Bullet                   # importujemy klasę Bullet reprezentującą pocisk

class Player(Unit):                                  # definiujemy klasę gracza dziedziczącą po Unit
    SPEED = 3                                       # stała prędkość ruchu gracza (piksele na klatkę)

    def __init__(self, position, sprite,bullet_sprite):
        super().__init__(position, sprite)          # wywołujemy konstruktor Unit z pozycją i grafiką
        self.velocity = pygame.math.Vector2(0, 0)    # wektor prędkości, na początku zerowy
        self.hp = 4                                # punkty życia gracza
        self.bullet_sprite = bullet_sprite

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
        return Bullet(
            self.rect.center,
            self.bullet_sprite,
            pygame.math.Vector2(0, -10)
        )

    def update(self):
        self.handle_input()                           # najpierw obsługujemy wejście od gracza
        self.rect.move_ip(self.velocity)              # przesuwamy prostokąt gracza o wektor prędkości

        # ograniczenie gracza do obszaru ekranu
        screen_rect = pygame.display.get_surface().get_rect()
                                                     # pobieramy prostokąt aktualnego ekranu
        self.rect.clamp_ip(screen_rect)               # ograniczamy rect gracza do wnętrza ekranu
