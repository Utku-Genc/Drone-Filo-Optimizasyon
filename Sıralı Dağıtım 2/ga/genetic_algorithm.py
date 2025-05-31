import random
from typing import List, Dict, Tuple, Optional
from models.drone import Drone
from models.delivery import DeliveryPoint
from models.noflyzone import NoFlyZone
from graph.utils import euclidean_distance

def generate_random_population(drones: List[Drone], deliveries: List[DeliveryPoint], population_size: int) -> List[Dict[int, int]]:
    population = []
    for _ in range(population_size):
        assignment = {}
        for delivery in deliveries:
            drone = random.choice(drones)
            assignment[delivery.id] = drone.id
        population.append(assignment)
    return population

def compute_total_energy(assignment: Dict[int, int], drones: List[Drone], deliveries: List[DeliveryPoint]) -> float:
    total_energy = 0
    drone_positions = {drone.id: drone.start_pos for drone in drones}
    for delivery_id, drone_id in assignment.items():
        delivery = next(d for d in deliveries if d.id == delivery_id)
        start_pos = drone_positions[drone_id]
        dist = euclidean_distance(start_pos, delivery.pos)
        # enerji = mesafe * ağırlık (basit)
        energy = dist * delivery.weight
        total_energy += energy
        # drone pozisyonunu güncelle 
        drone_positions[drone_id] = delivery.pos
    return total_energy

def count_constraint_violations(assignment: Dict[int, int], drones: List[Drone], deliveries: List[DeliveryPoint], 
                                no_fly_zones: List[NoFlyZone], current_time: float) -> int:
    violations = 0
    drone_carrying = {drone.id: 0 for drone in drones}
    for delivery_id, drone_id in assignment.items():
        delivery = next(d for d in deliveries if d.id == delivery_id)
        drone = next(dr for dr in drones if dr.id == drone_id)
        drone_carrying[drone_id] += 1
        if drone_carrying[drone_id] > 1:
            violations += 1
        if delivery.weight > drone.max_weight:
            violations += 1
        # no-fly zone kontrolü
        for zone in no_fly_zones:
            start_time, end_time = zone.active_time
            if start_time <= current_time <= end_time:
                xs, ys = zip(*zone.coordinates)
                if (min(xs) <= delivery.pos[0] <= max(xs)) and (min(ys) <= delivery.pos[1] <= max(ys)):
                    violations += 1
                    break
        # zaman penceresi kontrolü
        if not (delivery.time_window[0] <= current_time <= delivery.time_window[1]):
            violations += 1
    return violations

def fitness(assignment: Dict[int, int], drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone], current_time: float) -> float:
    delivered_count = len(assignment)
    total_energy = compute_total_energy(assignment, drones, deliveries)
    violations = count_constraint_violations(assignment, drones, deliveries, no_fly_zones, current_time)
    return (delivered_count * 50) - (total_energy * 0.1) - (violations * 1000)

def crossover(parent1: Dict[int, int], parent2: Dict[int, int]) -> Dict[int, int]:
    # Tek noktalı crossover
    child = {}
    delivery_ids = list(parent1.keys())
    crossover_point = random.randint(1, len(delivery_ids) - 1)
    for i, d_id in enumerate(delivery_ids):
        if i < crossover_point:
            child[d_id] = parent1[d_id]
        else:
            child[d_id] = parent2[d_id]
    return child

def mutate(assignment: Dict[int, int], drones: List[Drone], mutation_rate: float = 0.1) -> Dict[int, int]:
    mutated = assignment.copy()
    for delivery_id in mutated:
        if random.random() < mutation_rate:
            mutated[delivery_id] = random.choice(drones).id
    return mutated

def genetic_algorithm(drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone], current_time: float, population_size=50, generations=100) -> Dict[int, int]:
    population = generate_random_population(drones, deliveries, population_size)
    for _ in range(generations):
        population = sorted(population, key=lambda ind: fitness(ind, drones, deliveries, no_fly_zones, current_time), reverse=True)
        next_generation = population[:10]  # elitizm: en iyiler direkt
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(population[:20], 2)
            child = crossover(parent1, parent2)
            child = mutate(child, drones)
            next_generation.append(child)
        population = next_generation
    best = max(population, key=lambda ind: fitness(ind, drones, deliveries, no_fly_zones, current_time))
    return best
