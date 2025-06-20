import json
import os
from .config import HIGH_SCORE_FILE

class HighScore:
    def __init__(self):
        self.high_score = self.load_high_score()

    def load_high_score(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)['high_score']
            return 0
        except:
            return 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def update(self, score):
        if score > self.high_score:
            self.high_score = score
            self.save_high_score()
            return True
        return False 