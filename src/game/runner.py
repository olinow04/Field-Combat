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

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Field Combat Clone")

    show_start_screen(screen)  # <--- DODAJ TO WYWOŁANIE

    font = pygame.font.SysFont("Arial", 24)
    score_manager = ScoreManager()
    level_number = 1
    bg_color = (30, 30, 30)
    while True:
        level = Level(screen, level_number, score_manager, bg_color)
        result = level.run()
        draw_hud(screen, font, level.score, len(level.allies), level.player.hp)
        if result is None:
            break
        else:
            level_number, bg_color = result
        if level_number > NUM_LEVELS:
            break
    pygame.quit()
