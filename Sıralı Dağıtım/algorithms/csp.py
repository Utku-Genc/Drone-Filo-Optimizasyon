from typing import List, Dict, Tuple, Optional
from datetime import datetime, time
from dataclasses import dataclass
from core.drone import Drone
from core.delivery_point import DeliveryPoint
from core.no_fly_zone import NoFlyZone
from utils.geometry_utils import euclidean_distance
from utils.datetime_utils import time_to_seconds, add_seconds_to_time, parse_time, seconds_to_time # <<< Make sure seconds_to_time is imported here

from ortools.sat.python import cp_model

@dataclass
class PathInfo:
    points: List[Tuple[float, float]]
    length: float
    travel_time_seconds: float
    energy_consumption_mah: float
    valid: bool = True
    reason: str = ""

def calculate_path_info(
    start_pos: Tuple[float, float],
    end_pos: Tuple[float, float],
    drone_speed: float,
    drone_consumption_rate: float,
    no_fly_zones: List[NoFlyZone],
    current_sim_time: datetime.time,
    base_station_pos: Tuple[float, float]
) -> PathInfo:
    path_points = [start_pos, end_pos]
    total_distance = euclidean_distance(start_pos, end_pos)
    total_travel_time_seconds = total_distance / drone_speed if drone_speed > 0 else float('inf')
    total_energy_consumption_mah = drone_consumption_rate * total_travel_time_seconds

    for nfz in no_fly_zones:
        if nfz.is_active(current_sim_time):
            # sadece başlangıç veya bitiş noktası içindeyse geçersiz sayıyoruz.
            if nfz.contains_point(start_pos) or nfz.contains_point(end_pos) or \
               nfz.intersects_segment(start_pos, end_pos): 
                return PathInfo([], 0.0, 0.0, 0.0, False, f"NFZ {nfz.id} ile çakışıyor")


    return PathInfo(path_points, total_distance, total_travel_time_seconds, total_energy_consumption_mah, True)


def solve_assignment_csp(
    drones: List[Drone],
    deliveries: List[DeliveryPoint],
    no_fly_zones: List[NoFlyZone],
    current_sim_time: datetime.time,
    base_station_pos: Tuple[float, float] = (0.0, 0.0)
) -> List[Dict]:
    """
    Dronlar ve teslimatlar arasında optimal atama yapmak için bir CSP modeli (OR-Tools CP-SAT) kullanır.
    """
    model = cp_model.CpModel()

    # Değişkenler: x[d][t] = 1 eğer drone d teslimat t'ye atanırsa, aksi takdirde 0
    x = {}
    for d in drones:
        for t in deliveries:
            x[(d.id, t.id)] = model.NewBoolVar(f'x_d{d.id}_t{t.id}')

    # Kısıt 1: Her teslimat en fazla bir drone'a atanır
    for t in deliveries:
        model.AddAtMostOne(x[(d.id, t.id)] for d in drones)

    # Kısıt 2: Her drone en fazla bir teslimata atanır
    for d in drones:
        model.AddAtMostOne(x[(d.id, t.id)] for t in deliveries)

    # Yol bilgilerini önceden hesapla ve kısıtları ekle
    possible_assignments = []
    path_infos: Dict[Tuple[int, int], PathInfo] = {}

    for d in drones:
        for t in deliveries:
            if t.is_assigned: # Zaten atanmış teslimatları ele alma
                continue

            path_info = calculate_path_info(d.current_pos, t.pos, d.speed, d.consumption_rate, no_fly_zones, current_sim_time, base_station_pos)

            if not path_info.valid:
                # Yol NFZ nedeniyle geçersizse, bu atamayı yasakla
                model.Add(x[(d.id, t.id)] == 0)
                continue

            # Batarya kontrolü
            if d.current_battery < path_info.energy_consumption_mah:
                # Yeterli batarya yoksa bu atamayı yasakla
                model.Add(x[(d.id, t.id)] == 0)
                continue

            # Zaman penceresi kontrolü
            arrival_time_seconds = time_to_seconds(current_sim_time) + path_info.travel_time_seconds
            estimated_arrival_time = seconds_to_time(arrival_time_seconds) 

            if not t.is_within_time_window(estimated_arrival_time):
                model.Add(x[(d.id, t.id)] == 0)
                continue

            path_infos[(d.id, t.id)] = path_info
            possible_assignments.append((d.id, t.id))

    objective_terms = []
    for d_id, t_id in possible_assignments:
        delivery = next(t for t in deliveries if t.id == t_id)
        objective_terms.append(x[(d_id, t_id)] * delivery.priority)

    model.Maximize(sum(objective_terms))


    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = False 
    status = solver.Solve(model)

    results = []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for d_id, t_id in possible_assignments:
            if solver.Value(x[(d_id, t_id)]) == 1:
                results.append({
                    'drone_id': d_id,
                    'delivery_id': t_id,
                    'path_info': path_infos[(d_id, t_id)]
                })
        print(f"CSP Çözücü Durumu: {solver.StatusName(status)}, Toplam Amaç Değeri: {solver.ObjectiveValue()}")
    else:
        print(f"CSP Çözücü Durumu: {solver.StatusName(status)}")

    return results