class HighScoreManager:
    def __init__(self):
        # Inicjalizuje menedżera z domyślnym wynikiem 0.
        self.high_score = 0

    def save_score(self, score):
        # Zapisuje nowy wynik, jeśli jest wyższy od dotychczasowego rekordu.
        if score > self.high_score:
            self.high_score = score
        print(f"Score: {score} | High Score: {self.high_score}")
