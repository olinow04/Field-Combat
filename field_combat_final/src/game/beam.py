import pygame  # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń

class Beam(pygame.sprite.Sprite):  # definiujemy klasę promienia dziedziczącą po pygame.sprite.Sprite
    SPEED = 10             # prędkość ruchu promienia (pikseli na klatkę)
    WIDTH, HEIGHT = 10, 30  # szerokość i wysokość promienia w pikselach

    def __init__(self, start, target):
        super().__init__()
        # tworzymy obraz promienia o rozmiarze WIDTH×HEIGHT z kanałem alfa (przezroczystość)
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        # rysujemy prostokąt w kolorze cyjanowym (RGB 0,255,255) w obrębie całego surface
        pygame.draw.rect(self.image, (0, 255, 255), (0, 0, self.WIDTH, self.HEIGHT))
        # pobieramy prostokąt (rect) obrazka i ustawiamy jego środek na pozycji startowej
        self.rect = self.image.get_rect(center=start)

        # obliczamy wektor różnicy między pozycją celu a pozycją startową
        delta = pygame.math.Vector2(target) - pygame.math.Vector2(start)
        if delta.length() == 0:
            # jeśli start i cel są w tym samym miejscu, ustawiamy domyślny wektor w górę
            delta = pygame.math.Vector2(0, -1)
        # normalizujemy wektor, aby miał długość 1, zachowując tylko kierunek
        direction = delta.normalize()
        # mnożymy kierunek przez prędkość, otrzymując wektor prędkości
        self.velocity = direction * self.SPEED

    def update(self):
        # przesuwamy rect o obliczony wektor prędkości
        self.rect.move_ip(self.velocity)

        # pobieramy prostokąt ekranu z głównego surface wyświetlanego okna
        screen_rect = pygame.display.get_surface().get_rect()
        # jeśli promień opuścił obszar ekranu (brak kolizji rect z ekranem)
        if not screen_rect.colliderect(self.rect):
            # usuwamy ten sprite ze wszystkich grup, do których należy
            self.kill()
