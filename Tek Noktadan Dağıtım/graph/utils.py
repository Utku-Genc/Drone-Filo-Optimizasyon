import math
from typing import Tuple

def euclidean_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

def compute_cost(distance: float, weight: float, priority: int) -> float:
    # enerji = mesafe * ağırlık + öncelik cezası
    return distance * weight + (priority * 100)
