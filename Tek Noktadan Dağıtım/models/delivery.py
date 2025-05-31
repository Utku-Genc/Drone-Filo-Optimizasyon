from dataclasses import dataclass
from typing import Tuple

@dataclass
class DeliveryPoint:
    id: int
    pos: Tuple[float, float]
    weight: float
    priority: int
    time_window: Tuple[int, int]
