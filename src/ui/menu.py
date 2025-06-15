import pygame
from src.config import WHITE, BLACK, SCREEN_WIDTH
from src.ui.button import Button

class MenuStart:
    def __init__(self, screen):
        # Inicjalizuje menu startowe z ekranem, czcionką oraz przyciskami "Play" i "Exit"
        self.screen = screen
        self.font = pygame.font.SysFont(None, 72)
        self.buttons = [
            Button((300, 250, 200, 50), 'Play',   lambda: 'play'),
            Button((300, 350, 200, 50), 'Exit',   lambda: 'exit')
        ]

    def run(self):
        # Uruchamia pętlę menu startowego, obsługując zdarzenia i zwracając wynik wybranej opcji
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                for btn in self.buttons:
                    result = btn.handle_event(event)
                    if result == 'play':
                        return 1
                    elif result == 'exit':
                        return None

            self.screen.fill(WHITE)
            title = self.font.render('Field Combat', True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)

class MenuEnd:
    def __init__(self, screen, score):
        # Inicjalizuje menu końcowe z ekranem, wynikiem oraz przyciskami "Restart" i "Exit"
        self.screen = screen
        self.score = score
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [
            Button((300, 350, 200, 50), 'Restart', lambda: 'restart'),
            Button((300, 450, 200, 50), 'Exit',    lambda: 'exit')
        ]

    def run(self):
        # Uruchamia pętlę menu końcowego, obsługując zdarzenia i zwracając wybraną opcję
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'exit'
                for btn in self.buttons:
                    result = btn.handle_event(event)
                    if result:
                        return result

            self.screen.fill(WHITE)
            msg = self.font.render(f'Your Score: {self.score}', True, BLACK)
            self.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 200))
            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)
