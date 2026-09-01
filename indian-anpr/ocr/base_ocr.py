from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class BaseOCR(ABC):
    @abstractmethod
    def read_text(self, image: np.ndarray) -> Tuple[str, float]:
        pass
