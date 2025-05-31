import math
from typing import Tuple

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    # İki nokta arasındaki Öklid mesafesini hesaplar.
    
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)