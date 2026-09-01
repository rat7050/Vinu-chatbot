from collections import Counter, defaultdict
import time
from typing import Optional, Tuple


class TemporalVotingManager:
    def __init__(self, required_votes: int = 3, timeout_seconds: float = 8.0):
        self.required_votes = required_votes
        self.timeout_seconds = timeout_seconds
        self.history = defaultdict(list)
        self.confirmed_plates = {}

    def add_observation(self, track_id: int, plate_text: str, confidence: float):
        now = time.time()
        self.history[track_id].append((plate_text, confidence, now))
        self.history[track_id] = [
            obs for obs in self.history[track_id] if now - obs[2] <= self.timeout_seconds
        ]

    def get_confirmed_plate(self, track_id: int) -> Tuple[Optional[str], float]:
        if track_id in self.confirmed_plates:
            return self.confirmed_plates[track_id], 1.0

        records = self.history.get(track_id, [])
        if len(records) < self.required_votes:
            return None, 0.0

        score_map = defaultdict(float)
        count_map = Counter()

        for text, conf, _ in records:
            score_map[text] += conf
            count_map[text] += 1

        best_plate, best_count = count_map.most_common(1)[0]
        if best_count >= self.required_votes:
            avg_conf = score_map[best_plate] / best_count
            self.confirmed_plates[track_id] = best_plate
            return best_plate, avg_conf

        return None, 0.0
