from dataclasses import dataclass
from typing import Tuple

@dataclass
class Drone:
    id: int
    max_weight: float
    battery: int
    speed: float
    start_pos: Tuple[float, float]
