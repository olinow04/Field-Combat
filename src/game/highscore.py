class HighScoreManager:
    def __init__(self):
        self.high_score = 0

    def save_score(self, score):
        if score > self.high_score:
            self.high_score = score
        print(f"Score: {score} | High Score: {self.high_score}")