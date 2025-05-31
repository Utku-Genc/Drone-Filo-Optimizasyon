import heapq
from typing import List, Tuple, Optional, Callable
from core.drone import Drone
from core.delivery_point import DeliveryPoint
from core.no_fly_zone import NoFlyZone
from geometry_utils import euclidean_distance, check_path_for_nfz_intersections
from datetime_utils import time # datetime.time objesi için


class AStarPath:
    """A* tarafından bulunan bir yolu ve maliyetini saklar."""
    def __init__(self, points: List[Tuple[float, float]], length: float):
        self.points = points # [(x1,y1), (x2,y2), ...]
        self.length = length # Metre cinsinden toplam uzunluk

def find_path_astar(
    start_pos: Tuple[float, float],
    goal_pos: Tuple[float, float],
    drone: Drone, # Batarya kontrolü için
    delivery: DeliveryPoint, # Ağırlık ve öncelik için (maliyet fonksiyonunda kullanılacak)
    no_fly_zones: List[NoFlyZone],
    current_time: time
) -> Optional[AStarPath]:
    
    distance = euclidean_distance(start_pos, goal_pos)

    # 1. Batarya Kontrolü
    if not drone.has_enough_battery(distance):
        return None

    # 2. No-Fly Zone Kontrolü
    path_crosses_nfz = check_path_for_nfz_intersections(start_pos, goal_pos, no_fly_zones, current_time)
    
    if path_crosses_nfz:
        return None # NFZ'den geçen yollar kabul edilmez

    # Düz yol geçerli ise
    path = AStarPath(points=[start_pos, goal_pos], length=distance)
    return path


def a_star_heuristic_cost(
    start_pos: Tuple[float, float],
    goal_pos: Tuple[float, float],
    no_fly_zones: List[NoFlyZone],
    current_time: time,
    base_penalty_nfz: float = 10000.0 # NFZ kesişimi için temel ceza
    ) -> float:

    distance_to_target = euclidean_distance(start_pos, goal_pos)
    penalty = 0
    if check_path_for_nfz_intersections(start_pos, goal_pos, no_fly_zones, current_time):
        penalty = base_penalty_nfz #ceza ekle
    return distance_to_target + penalty


def a_star_delivery_cost(
    distance: float, 
    weight: float, 
    priority: int 
    ) -> float:
    """
    Maliyet Fonksiyonu: distance * weight + (6 - priority) * 100
    """
    # Öncelik 1 (en yüksek) daha düşük maliyet, 5 (en düşük) daha yüksek maliyet verir.
    priority_penalty_multiplier = 100 

    cost = (distance * weight) + ((6 - priority) * priority_penalty_multiplier)
    return cost
