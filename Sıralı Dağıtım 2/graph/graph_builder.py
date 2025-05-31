from typing import List, Dict, Tuple
from models.drone import Drone
from models.delivery import DeliveryPoint
from graph.utils import euclidean_distance, compute_cost

def build_graph(drones: List[Drone], deliveries: List[DeliveryPoint]) -> Dict[str, List[Tuple[str, float]]]:
    graph: Dict[str, List[Tuple[str, float]]] = {}

    # Drone -> Teslimat bağlantıları
    for drone in drones:
        drone_key = f"D{drone.id}"
        graph[drone_key] = []
        for delivery in deliveries:
            if delivery.weight <= drone.max_weight:
                dist = euclidean_distance(drone.start_pos, delivery.pos)
                cost = compute_cost(dist, delivery.weight, delivery.priority)
                graph[drone_key].append((f"DP{delivery.id}", cost))

    # Teslimat -> Teslimat bağlantıları
    for delivery1 in deliveries:
        d1_key = f"DP{delivery1.id}"
        if d1_key not in graph:
            graph[d1_key] = []
        for delivery2 in deliveries:
            if delivery1.id != delivery2.id:
                dist = euclidean_distance(delivery1.pos, delivery2.pos)
                cost = compute_cost(dist, delivery2.weight, delivery2.priority)
                graph[d1_key].append((f"DP{delivery2.id}", cost))

    return graph
