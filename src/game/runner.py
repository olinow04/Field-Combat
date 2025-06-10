# src/game/runner.py

import pygame
from src.game.level import Level
from src.config import NUM_LEVELS
from src.utils.score import ScoreManager
from src.game.hud import draw_hud
import os

def show_start_screen(screen):
    # Ustal ścieżkę do katalogu głównego projektu względem tego pliku
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    image_path = os.path.join(project_root, 'image', 'startup_screen.png')
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Nie znaleziono pliku startowego: {image_path}")
    startup_img = pygame.image.load(image_path)
    startup_img = pygame.transform.scale(startup_img, (800, 600))

    font = pygame.font.SysFont("Arial", 36)
    press_start = font.render("Press any key to start", True, (255, 255, 255))
    press_start_rect = press_start.get_rect(center=(400, 500))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        screen.blit(startup_img, (0, 0))
        screen.blit(press_start, press_start_rect)
        pygame.display.flip()


def show_end_screen(screen, score, is_victory):
    screen.fill((0, 0, 0))
    font_big = pygame.font.SysFont("Arial", 48)
    font = pygame.font.SysFont("Arial", 24)

    # Nagłówek
    title = "GRATULACJE!" if is_victory else "KONIEC GRY"
    title_surf = font_big.render(title, True, (255, 255, 0))
    title_rect = title_surf.get_rect(centerx=screen.get_width() // 2, y=100)
    screen.blit(title_surf, title_rect)

    # Wynik końcowy
    score_text = f"Końcowy wynik: {score}"
    score_surf = font.render(score_text, True, (255, 255, 255))
    score_rect = score_surf.get_rect(centerx=screen.get_width() // 2, y=200)
    screen.blit(score_surf, score_rect)

    # Instrukcja wyjścia
    exit_surf = font.render("Naciśnij ENTER aby wyjść", True, (128, 128, 128))
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
    pygame.display.set_caption("Field Combat Clone")

    show_start_screen(screen)

    font = pygame.font.SysFont("Arial", 24)
    score_manager = ScoreManager()
    level_number = 1
    bg_color = (30, 30, 30)
    final_score = 0

    while True:
        level = Level(screen, level_number, score_manager, bg_color)
        result = level.run()
        if result is None:
            # Przegrana
            show_end_screen(screen, level.score, False)
            break
        else:
            level_number, bg_color = result
            final_score = level.score

        if level_number > NUM_LEVELS:
            # Wygrana - wszystkie poziomy ukończone
            show_end_screen(screen, final_score, True)
            break

    pygame.quit()
