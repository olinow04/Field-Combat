class ScoreManager:
    def __init__(self):
        # Inicjalizuje menadżera wyniku z wartością początkową 0
        self.score = 0

    def add_score(self, points):
        # Dodaje określoną liczbę punktów do bieżącego wyniku
        self.score += points

    def get_current_score(self):
        # Zwraca aktualny wynik
        return self.score

    def get_score(self):
        # Zwraca aktualny wynik (alias get_current_score)
        return self.score

    def save_score(self, score):
        # Zapisuje najwyższy wynik spośród obecnego i podanego
        self.score = max(self.score, score)

    def reset_score(self):
        # Resetuje wynik do zera
        self.score = 0
