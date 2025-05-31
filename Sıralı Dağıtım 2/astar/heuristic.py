from typing import Dict, List
from graph.utils import euclidean_distance
from models.delivery import DeliveryPoint

def heuristic(node: str, goal: str, deliveries: List[DeliveryPoint]) -> float:

    def get_pos(n: str):
        if n.startswith("D"):
            # drone start pozisyonu bilgisi dışarıdan lazım, şimdilik (0,0)
            return (0, 0)
        elif n.startswith("DP"):
            delivery_id = int(n[2:])
            dp = next((d for d in deliveries if d.id == delivery_id), None)
            if dp:
                return dp.pos
        return (0, 0)

    pos_node = get_pos(node)
    pos_goal = get_pos(goal)
    return euclidean_distance(pos_node, pos_goal)
