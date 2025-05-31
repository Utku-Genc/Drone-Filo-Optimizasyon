import random
from typing import List, Dict, Tuple, Callable, Any, Optional
from core.drone import Drone
from core.delivery_point import DeliveryPoint
from core.no_fly_zone import NoFlyZone
from algorithms.a_star import find_path_astar, a_star_delivery_cost
from geometry_utils import euclidean_distance
from datetime_utils import time as وقت, add_seconds_to_time, time_to_seconds

# Bir drone için rota (teslimat sıralaması)
Chromosome = List[int] 
def calculate_sequence_fitness(
    chromosome: Chromosome, # Teslimat ID'lerinin sıralaması
    drone_initial_state: Drone, # Drone'un bu sekansa başlamadan önceki durumu
    deliveries_dict: Dict[int, DeliveryPoint],
    no_fly_zones: List[NoFlyZone],
    initial_time: وقت,
    base_start_pos: Tuple[float,float] # Şarj vb için üs konumu
) -> Tuple[float, int, float, int]: # fitness, num_deliveries, total_energy, total_violations

    num_deliveries_completed = 0
    total_energy_used = 0.0 # mAh
    total_violations = 0 # Zaman penceresi, NFZ (yol bulunamazsa)

    current_pos = drone_initial_state.current_pos
    current_battery = drone_initial_state.current_battery
    current_time = initial_time
    
    drone_speed = drone_initial_state.speed
    drone_consumption_rate = drone_initial_state.consumption_rate

    temp_drone_for_calc = Drone(
        id=drone_initial_state.id,
        max_weight=drone_initial_state.max_weight, 
        battery_capacity=drone_initial_state.battery_capacity,
        speed=drone_speed,
        start_pos=current_pos,
        consumption_rate=drone_consumption_rate,
        charge_time_per_mah=drone_initial_state.charge_time_per_mah
    )
    temp_drone_for_calc.current_battery = current_battery


    for delivery_id in chromosome:
        delivery = deliveries_dict[delivery_id]

        path_info = find_path_astar(current_pos, delivery.pos, temp_drone_for_calc, delivery, no_fly_zones, current_time)

        if path_info is None: 
            total_violations += 1 
            break 
        
        distance = path_info.length
        flight_time_seconds = temp_drone_for_calc.calculate_flight_time(distance)
        energy_consumed = temp_drone_for_calc.calculate_battery_consumption(flight_time_seconds)

        # Batarya kontrolü tekrar teyit
        if temp_drone_for_calc.current_battery < energy_consumed:
            total_violations +=1 # Batarya yetmedi
            break

        # Zaman penceresi kontrolü
        estimated_arrival_time = add_seconds_to_time(current_time, flight_time_seconds)
        if not delivery.is_within_time_window(estimated_arrival_time):
            total_violations += 1 
        # Teslimat başarılı 
        temp_drone_for_calc.current_battery -= energy_consumed
        total_energy_used += energy_consumed
        current_pos = delivery.pos
        current_time = add_seconds_to_time(estimated_arrival_time, random.uniform(30,90)) # Teslimat süresi için küçük bir ekleme
        num_deliveries_completed += 1

    fitness = (num_deliveries_completed * 100.0) - (total_energy_used * 0.2) - (total_violations * 2000.0)
    
    return fitness, num_deliveries_completed, total_energy_used, total_violations


def initialize_population(assigned_deliveries: List[int], population_size: int) -> List[Chromosome]:
    population = []
    for _ in range(population_size):
        chromosome = random.sample(assigned_deliveries, len(assigned_deliveries))
        population.append(chromosome)
    return population

def selection(population: List[Chromosome], fitness_scores: List[float], num_parents: int) -> List[Chromosome]:
    parents = []
    tournament_size = max(2, len(population) // 10)

    
    for _ in range(num_parents):
        tournament_contenders_indices = random.sample(range(len(population)), tournament_size)
        winner_index = -1
        best_fitness_in_tournament = -float('inf')
        for contender_idx in tournament_contenders_indices:
            if fitness_scores[contender_idx] > best_fitness_in_tournament:
                best_fitness_in_tournament = fitness_scores[contender_idx]
                winner_index = contender_idx
        if winner_index != -1:
            parents.append(population[winner_index])
        else: 
            parents.append(random.choice(population))
            
    return parents


def crossover_ordered(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
    size = len(parent1)
    child1, child2 = [-1]*size, [-1]*size

    start, end = sorted(random.sample(range(size), 2))

    child1[start:end+1] = parent1[start:end+1]
    child2[start:end+1] = parent2[start:end+1]

    def fill_child(child, parent, current_parent_elements):
        parent_idx = 0
        for i in range(size):
            if child[i] == -1: 
                while parent[parent_idx] in current_parent_elements: 
                    parent_idx = (parent_idx + 1) % size
                child[i] = parent[parent_idx]
                parent_idx = (parent_idx + 1) % size
        return child

    child1 = fill_child(child1, parent2, set(child1[start:end+1]))
    child2 = fill_child(child2, parent1, set(child2[start:end+1]))
    
    return child1, child2


def mutate_swap(chromosome: Chromosome, mutation_rate: float) -> Chromosome:
    if random.random() < mutation_rate and len(chromosome) >= 2:
        idx1, idx2 = random.sample(range(len(chromosome)), 2)
        chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
    return chromosome


def run_genetic_algorithm(
    drone: Drone, # Optimize edilecek drone
    assigned_delivery_ids: List[int], # Bu drone'a atanmış teslimat ID'leri
    all_deliveries_dict: Dict[int, DeliveryPoint], # Tüm teslimatların haritası
    no_fly_zones: List[NoFlyZone],
    current_sim_time: وقت,
    base_station_pos: Tuple[float,float],
    generations: int = 100,
    population_size: int = 50,
    mutation_rate: float = 0.1,
    crossover_rate: float = 0.8, 
    num_elites: int = 2 
) -> Tuple[Optional[Chromosome], float]:
    """
    Belirli bir drone için teslimat sıralamasını optimize eder.
    Returns: En iyi rota (teslimat ID listesi) ve fitness değeri.
    """
    if not assigned_delivery_ids:
        return None, -float('inf')
    if len(assigned_delivery_ids) == 1: 
        fitness, _, _, _ = calculate_sequence_fitness(
            assigned_delivery_ids, drone, all_deliveries_dict, no_fly_zones, current_sim_time, base_station_pos
        )
        return assigned_delivery_ids, fitness

    population = initialize_population(assigned_delivery_ids, population_size)
    best_chromosome_overall = None
    best_fitness_overall = -float('inf')

    for gen in range(generations):
        fitness_scores = [
            calculate_sequence_fitness(chromo, drone, all_deliveries_dict, no_fly_zones, current_sim_time, base_station_pos)[0]
            for chromo in population
        ]

        # En iyileri bul ve sakla
        sorted_population_with_scores = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)
        
        if sorted_population_with_scores[0][1] > best_fitness_overall:
            best_fitness_overall = sorted_population_with_scores[0][1]
            best_chromosome_overall = sorted_population_with_scores[0][0]

        next_generation = []

        for i in range(min(num_elites, len(sorted_population_with_scores))):
            next_generation.append(sorted_population_with_scores[i][0])
            
        num_parents_to_select = population_size - len(next_generation)
        if num_parents_to_select % 2 != 0 and num_parents_to_select > 0 : 
             num_parents_to_select = max(0, num_parents_to_select -1) if population_size > len(next_generation) else 0
        
        if num_parents_to_select > 0 :
            parents = selection(population, fitness_scores, num_parents_to_select)

            for i in range(0, len(parents) -1, 2): 
                parent1, parent2 = parents[i], parents[i+1]
                if random.random() < crossover_rate:
                    child1, child2 = crossover_ordered(parent1, parent2)
                    next_generation.extend([child1, child2])
                else: 
                    next_generation.extend([parent1, parent2])
        
        for i in range(num_elites, len(next_generation)): 
            next_generation[i] = mutate_swap(next_generation[i], mutation_rate)

        if len(next_generation) < population_size and population:
             needed = population_size - len(next_generation)
             fillers = [p[0] for p in sorted_population_with_scores[:needed]]
             next_generation.extend(fillers)

        population = next_generation[:population_size] 

        if gen % 10 == 0:
             print(f"GA Gen {gen}: Best Fitness = {best_fitness_overall:.2f}, Pop Size: {len(population)}")

    print(f"GA Tamamlandı. En İyi Rota: {best_chromosome_overall}, Fitness: {best_fitness_overall:.2f}")
    return best_chromosome_overall, best_fitness_overall