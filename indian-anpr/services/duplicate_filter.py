import time
from typing import Dict


class DuplicateFilter:
    def __init__(self, cooldown_seconds: float = 10.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_saved: Dict[str, float] = {}

    def should_save(self, plate_number: str) -> bool:
        now = time.time()
        if plate_number not in self.last_saved:
            self.last_saved[plate_number] = now
            return True

        if now - self.last_saved[plate_number] >= self.cooldown_seconds:
            self.last_saved[plate_number] = now
            return True

        return False
