from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class NoFlyZone:
    id: int
    coordinates: List[Tuple[float, float]]
    active_time: Tuple[int, int]
