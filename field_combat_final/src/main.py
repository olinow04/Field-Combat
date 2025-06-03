import pygame  # importujemy bibliotekę pygame do obsługi grafiki i zdarzeń
from game.level import Level  # importujemy klasę Level obsługującą logikę poziomu
from src.config import NUM_LEVELS

class ScoreManager:  # definiujemy klasę do zarządzania wynikami gry
    def __init__(self):
        self.high_score = 0  # inicjalizujemy najlepszy wynik na zero

    def save_score(self, score):
        # sprawdzamy, czy obecny wynik jest wyższy od dotychczasowego najlepszego
        if score > self.high_score:
            self.high_score = score  # aktualizujemy najlepszy wynik
        # wypisujemy aktualny i najlepszy wynik w konsoli
        print(f"Score: {score} | High Score: {self.high_score}")

def draw_hud(screen, font, score, allies_count, lives):
    # tworzymy napisy HUD: wynik, liczba sojuszników i liczba żyć
    score_surf = font.render(f"Wynik: {score}", True, (255, 255, 255))       # biały tekst
    allies_surf = font.render(f"Sojusznicy: {allies_count}", True, (0, 255, 0))  # zielony tekst
    lives_surf = font.render(f"Życia: {lives}", True, (255, 0, 0))           # czerwony tekst
    # rysujemy teksty w określonych pozycjach na ekranie
    screen.blit(score_surf, (10, 10))  # rysujemy wynik w lewym górnym rogu
    screen.blit(allies_surf, (10, 40))  # pod wynikiem rysujemy liczbę sojuszników
    screen.blit(lives_surf, (10, 70))  # pod sojusznikami rysujemy liczbę żyć

def main():
    # inicjalizacja modułów pygame
    pygame.init()  # uruchamiamy wszystkie moduły pygame
    screen = pygame.display.set_mode((800, 600))  # tworzymy okno gry o rozmiarze 800×600
    pygame.display.set_caption("Field Combat Clone")  # ustawiamy tytuł okna
    font = pygame.font.SysFont("Arial", 24)  # tworzymy czcionkę Arial o rozmiarze 24
    score_manager = ScoreManager()  # tworzymy obiekt do zarządzania wynikami
    level_number = 1  # zaczynamy od poziomu numer 1
    bg_color = (30, 30, 30)  # początkowy kolor tła (ciemnoszary)

    # główna pętla gry, wykonuje kolejne poziomy aż do zakończenia
    while True:
        # tworzymy i uruchamiamy nowy poziom
        level = Level(screen, level_number, score_manager, bg_color)
        result = level.run()  # uruchamiamy pętlę poziomu, zwraca None lub (nowy_numer, nowy_kolor)

        # rysujemy HUD po zakończeniu poziomu
        draw_hud(screen, font, level.score, len(level.allies), level.player.hp)

        # sprawdzamy rezultat poziomu
        if result is None:  # jeśli None, to zakończenie gry
            break  # wychodzimy z pętli głównej
        else:  # w przeciwnym razie przechodzimy do następnego poziomu
            level_number, bg_color = result  # aktualizujemy numer poziomu i kolor tła
        if level_number > NUM_LEVELS:
            break
    pygame.quit()  # zamykamy pygame i zwalniamy zasoby

if __name__ == "__main__":
    main()  # uruchamiamy funkcję main, jeśli skrypt jest wykonany bezpośrednio
