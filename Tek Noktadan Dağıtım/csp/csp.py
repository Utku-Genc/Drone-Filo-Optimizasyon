from typing import List, Dict, Optional
from models.drone import Drone
from models.delivery import DeliveryPoint
from models.noflyzone import NoFlyZone

def is_point_in_no_fly_zones(point: tuple, no_fly_zones: List[NoFlyZone], current_time: float) -> bool:
    for zone in no_fly_zones:
        start_time, end_time = zone.active_time
        if start_time <= current_time <= end_time:
            xs, ys = zip(*zone.coordinates)
            if (min(xs) <= point[0] <= max(xs)) and (min(ys) <= point[1] <= max(ys)):
                return True
    return False

def check_constraints(assignment: Dict[int, int], drones: List[Drone], deliveries: List[DeliveryPoint], 
                      no_fly_zones: List[NoFlyZone], current_time: float) -> bool:

    # 1. Drone kapasitesi kontrolü ve no-fly zone kontrolü
    drone_carrying = {drone.id: 0 for drone in drones}  # kaç teslimat taşıyor (max 1)
    
    for delivery_id, drone_id in assignment.items():
        delivery = next((d for d in deliveries if d.id == delivery_id), None)
        drone = next((dr for dr in drones if dr.id == drone_id), None)
        if not delivery or not drone:
            return False
        
        # Drone sadece 1 teslimat taşıyabilir (kısıt)
        drone_carrying[drone_id] += 1
        if drone_carrying[drone_id] > 1:
            return False
        
        # Kargo ağırlığı drone kapasitesini aşamaz
        if delivery.weight > drone.max_weight:
            return False
        
        # Teslimat no-fly zone içinde olamaz
        if is_point_in_no_fly_zones(delivery.pos, no_fly_zones, current_time):
            return False
        
        # Teslimat zaman penceresi kontrolü 
        if not (delivery.time_window[0] <= current_time <= delivery.time_window[1]):
            return False

    return True

def backtracking_search(drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone], current_time: float) -> Optional[Dict[int, int]]:

    assignment = {}

    def backtrack(index=0) -> bool:
        if index == len(deliveries):
            return True
        
        delivery = deliveries[index]
        for drone in drones:
            assignment[delivery.id] = drone.id
            if check_constraints(assignment, drones, deliveries, no_fly_zones, current_time):
                if backtrack(index + 1):
                    return True
            assignment.pop(delivery.id)
        return False

    if backtrack():
        return assignment
    else:
        return None
