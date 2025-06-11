import pygame


class Explosion(pygame.sprite.Sprite):
    """
    Klasa reprezentująca efekt eksplozji.
    Wykorzystuje dwie klatki animacji: oryginalny obrazek i jego odbicie.
    """
    images = []  # Lista przechowująca klatki animacji, inicjowana w Level.__init__

    def __init__(self, pos):
        """
        Inicjalizuje nową eksplozję.
        Args:
            pos: Tuple (x, y) określający pozycję środka eksplozji
        """
        super().__init__()

        # Pierwsza klatka animacji
        self.image = self.images[0]
        # Ustawienie prostokąta w miejscu eksplozji
        self.rect = self.image.get_rect(center=pos)
        # Czas ostatniej aktualizacji
        self.last_update = pygame.time.get_ticks()
        # Opóźnienie między klatkami (w milisekundach)
        self.frame_rate = 50
        # Indeks aktualnej klatki
        self.frame_index = 0
        # Całkowity czas życia eksplozji (w milisekundach)
        self.lifetime = 200

    def update(self):
        """
        Aktualizuje animację eksplozji.
        Zmienia klatki animacji zgodnie z frame_rate.
        Usuwa eksplozję po zakończeniu czasu życia.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            # Przełączanie między klatkami animacji
            self.frame_index = (self.frame_index + 1) % len(self.images)
            center = self.rect.center
            self.image = self.images[self.frame_index]
            self.rect = self.image.get_rect(center=center)
            # Zmniejszamy czas życia
            self.lifetime -= self.frame_rate
            if self.lifetime <= 0:
                self.kill()