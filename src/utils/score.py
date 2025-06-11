class ScoreManager:
    def __init__(self):
        self.score = 0

    def add_score(self, points):
        """Dodaje punkty do wyniku"""
        self.score += points

    def get_current_score(self):
        """Zwraca aktualny wynik"""
        return self.score

    def get_score(self):
        """Alias dla get_current_score()"""
        return self.score

    def save_score(self, score):
        """Zapisuje wynik (dla kompatybilności)"""
        self.score = max(self.score, score)

    def reset_score(self):
        """Resetuje wynik do zera"""
        self.score = 0