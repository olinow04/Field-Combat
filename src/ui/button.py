# ui/button.py
import pygame

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        txt = self.font.render(self.text, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return self.callback()
        return None
