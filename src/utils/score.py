import os

class ScoreManager:
    def __init__(self, filename='scores.txt'):
        self.filename = filename
        self.scores = []
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                for line in f:
                    try:
                        self.scores.append(int(line.strip()))
                    except ValueError:
                        pass

    def save_score(self, score):
        self.scores.append(score)
        with open(self.filename, 'a') as f:
            f.write(f"{score}\n")
