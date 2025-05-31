import heapq
from typing import Dict, List, Tuple
from models.delivery import DeliveryPoint
from models.drone import Drone
from models.noflyzone import NoFlyZone
from astar.heuristic import heuristic

def a_star(start_id: str, goal_id: str, graph: Dict[str, List[Tuple[str, float]]], 
           drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone], 
           current_time: float) -> List[str]:
    
    open_set = []
    heapq.heappush(open_set, (0, start_id))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start_id] = 0

    while open_set:
        current_f, current = heapq.heappop(open_set)
        if current == goal_id:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for neighbor, cost in graph.get(current, []):
            # No-fly zone kontrolü: eğer teslimat noktası no-fly zone içindeyse atla
            if neighbor.startswith("DP"):
                delivery_id = int(neighbor[2:])
                delivery = next((d for d in deliveries if d.id == delivery_id), None)
                if delivery:
                    for zone in no_fly_zones:
                        start_time, end_time = zone.active_time
                        if start_time <= current_time <= end_time:
                            xs, ys = zip(*zone.coordinates)
                            if (min(xs) <= delivery.pos[0] <= max(xs)) and (min(ys) <= delivery.pos[1] <= max(ys)):
                                # No-fly zone içinde, geçilemez
                                continue

            tentative_g_score = g_score[current] + cost
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal_id, deliveries)
                heapq.heappush(open_set, (f_score, neighbor))
    return []
