# src/game/hud.py

import pygame

def draw_hud(screen, font, score, allies_count, lives):
    score_surf = font.render(f"Wynik: {score}", True, (255, 255, 255))
    allies_surf = font.render(f"Sojusznicy: {allies_count}", True, (0, 255, 0))
    lives_surf = font.render(f"Życia: {lives}", True, (255, 0, 0))
    screen.blit(score_surf, (10, 10))
    screen.blit(allies_surf, (10, 40))
    screen.blit(lives_surf, (10, 70))
