import pygame
import os
from .level import Level
from src.utils.score import ScoreManager
from .audio_manager import get_audio_manager


def show_start_screen(screen):
    """Wyświetla ekran startowy z grafiką startup_screen.png"""
    # Pobierz audio manager
    audio = get_audio_manager()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Wypełnij ekran czarnym kolorem
    screen.fill((0, 0, 0))

    font_big = pygame.font.SysFont("Arial", 48)
    font = pygame.font.SysFont("Arial", 24)

    # Wczytaj grafikę startup_screen.png
    try:
        startup_screen_path = os.path.join(project_root, 'image', 'startup_screen.png')
        startup_screen_img = pygame.image.load(startup_screen_path).convert_alpha()
        startup_screen_img = pygame.transform.scale(startup_screen_img, (800, 600))
        startup_screen_rect = startup_screen_img.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(startup_screen_img, startup_screen_rect)
    except pygame.error:
        # Fallback do tekstu jeśli grafika nie istnieje
        title = "Field Combat"
        title_surf = font_big.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(centerx=screen.get_width() // 2, y=200)
        screen.blit(title_surf, title_rect)

        subtitle = "Gra strategiczna"
        subtitle_surf = font.render(subtitle, True, (200, 200, 200))
        subtitle_rect = subtitle_surf.get_rect(centerx=screen.get_width() // 2, y=280)
        screen.blit(subtitle_surf, subtitle_rect)

    # Instrukcja startu
    start_surf = font.render("Naciśnij ENTER aby rozpocząć grę", True, (255, 255, 0))
    start_rect = start_surf.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 50)
    screen.blit(start_surf, start_rect)

    # Instrukcja wyjścia
    exit_surf = font.render("ESC - wyjście", True, (128, 128, 128))
    exit_rect = exit_surf.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 20)
    screen.blit(exit_surf, exit_rect)

    pygame.display.flip()

    # Pętla oczekiwania na input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Zamknij grę
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True  # Rozpocznij grę
                elif event.key == pygame.K_ESCAPE:
                    return False  # Zamknij grę

        pygame.time.wait(10)


def show_end_screen(screen, score, is_victory):
    # Pobierz audio manager
    audio = get_audio_manager()

    # Zatrzymaj muzykę w tle
    audio.stop_background_music()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    screen.fill((0, 0, 0))

    font_big = pygame.font.SysFont("Arial", 48)
    font = pygame.font.SysFont("Arial", 24)

    if is_victory:
        # Odtwórz dźwięk końca gry przy zwycięstwie
        audio.play_sound('end_game_audio')

        # Wczytaj grafikę end_screen.png dla zwycięstwa
        try:
            end_screen_path = os.path.join(project_root, 'image', 'end_screen.png')
            end_screen_img = pygame.image.load(end_screen_path).convert_alpha()
            end_screen_img = pygame.transform.scale(end_screen_img, (800, 600))
            end_screen_rect = end_screen_img.get_rect(centerx=screen.get_width() // 2, y=50)
            screen.blit(end_screen_img, end_screen_rect)
        except pygame.error:
            # Fallback do tekstu jeśli grafika nie istnieje
            title = "Zwycięstwo!"
            title_surf = font_big.render(title, True, (0, 255, 0))
            title_rect = title_surf.get_rect(centerx=screen.get_width() // 2, y=100)
            screen.blit(title_surf, title_rect)
    else:
        # Przegrana - użyj grafiki game_over.png (game_over_audio już się odtwarza w level.py)
        try:
            game_over_path = os.path.join(project_root, 'image', 'game_over.png')
            game_over_img = pygame.image.load(game_over_path).convert_alpha()
            game_over_img = pygame.transform.scale(game_over_img, (800, 600))
            game_over_rect = game_over_img.get_rect(centerx=screen.get_width() // 2, y=50)
            screen.blit(game_over_img, game_over_rect)
        except pygame.error:
            # Fallback do tekstu
            title = "Koniec gry"
            title_surf = font_big.render(title, True, (255, 0, 0))
            title_rect = title_surf.get_rect(centerx=screen.get_width() // 2, y=100)
            screen.blit(title_surf, title_rect)

    # Wyświetl wynik końcowy
    score_text = f"Final Score: {score}"
    score_surf = font.render(score_text, True, (255, 255, 255))
    score_rect = score_surf.get_rect(centerx=screen.get_width() // 2, y=490)
    screen.blit(score_surf, score_rect)

    # Instrukcja wyjścia
    exit_surf = font.render("press ENTER to exit", True, (128, 128, 128))
    exit_rect = exit_surf.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 50)
    screen.blit(exit_surf, exit_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        pygame.time.wait(10)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Field Combat")

    # DODANY EKRAN STARTOWY
    if not show_start_screen(screen):
        pygame.quit()
        return

    score_manager = ScoreManager()
    level_number = 1
    max_levels = 3  # DODAJ LIMIT POZIOMÓW

    while True:
        level = Level(screen, level_number, score_manager)
        result = level.run()

        if result == "next_level":
            level_number += 1
            # ZMIEŃ TĘ SEKCJĘ:
            if level_number > max_levels:  # Sprawdź czy to ostatni poziom
                # Zatrzymaj wszystkie dźwięki przed końcowym ekranem
                audio = get_audio_manager()
                audio.stop_background_music()
                show_end_screen(screen, score_manager.score, True)
                break
        elif result == "game_over" or result is None:
            show_end_screen(screen, score_manager.score, False)
            break

    pygame.quit()


if __name__ == "__main__":
    main()