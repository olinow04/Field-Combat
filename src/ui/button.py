import pygame

class Button:
    def __init__(self, rect, text, callback):
        # Inicjalizuje przycisk z prostokątem, tekstem i funkcją wywoływaną po kliknięciu
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        # Rysuje przycisk na podanej powierzchni wraz z tekstem wyśrodkowanym w prostokącie
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        txt = self.font.render(self.text, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        # Obsługuje zdarzenie kliknięcia myszką, wywołując callback jeśli kliknięto przycisk
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return self.callback()
        return None
