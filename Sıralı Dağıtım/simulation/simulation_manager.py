import time as pytime
from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple, Optional
from core.drone import Drone
from core.delivery_point import DeliveryPoint
from core.no_fly_zone import NoFlyZone
from algorithms.csp import solve_assignment_csp, PathInfo
from utils.geometry_utils import euclidean_distance
from utils.datetime_utils import add_seconds_to_time, time_to_seconds, parse_time, seconds_to_time

class SimulationManager:
    """
    Simülasyonun ana akışını, verilerini ve performans metriklerini yöneten sınıf.
    """
    # --- Sabitler ---
    SIMULATION_START_TIME_STR = "00:00:00"
    SIMULATION_END_TIME_STR = "23:59:59"
    SIMULATION_STEP_SECONDS = 60  # saniye
    BASE_STATION_POS = (0.0, 0.0)
    DRONE_CHARGE_THRESHOLD_PERCENT = 0.20
    DRONE_MIN_CHARGE_FOR_NEW_TASK_PERCENT = 0.80

    def __init__(self):
        # --- Simülasyon Verileri ---
        self.drones: List[Drone] = []
        self.deliveries: List[DeliveryPoint] = []
        self.no_fly_zones: List[NoFlyZone] = []
        self.deliveries_dict: Dict[int, DeliveryPoint] = {} # Hızlı erişim için

        # --- Performans Metrikleri ---
        self.total_deliveries_made = 0
        self.total_energy_consumed_mah = 0.0
        self.total_flight_distance_meters = 0.0
        self.failed_deliveries_time_window = 0
        self.failed_deliveries_battery_csp = 0 
        self.failed_deliveries_nfz_csp = 0 
        self.failed_deliveries_path_issue = 0
        self.failed_deliveries_battery_midway = 0
        self.failed_deliveries_battery_mid_step = 0
        self.failed_deliveries_path_incomplete = 0

        # --- Simülasyon Durumu ---
        self.current_sim_time_obj: Optional[time] = None
        self.simulation_end_time_obj: Optional[time] = None
        self.drone_paths_history: Dict[int, List[List[Tuple[float, float]]]] = {}
        self.active_drone_segments: Dict[int, List[Tuple[float, float]]] = {}

    def load_data_from_dict(self, data_dict: dict):
        # verilerini yükler ve Drone, DeliveryPoint, NoFlyZone nesneleri oluşturur.
        loaded_drones = []
        loaded_deliveries = []
        loaded_nfzs = []

        sim_start_datetime_obj = datetime.strptime(self.SIMULATION_START_TIME_STR, "%H:%M:%S")

        default_consumption_rate = 1.0
        default_charge_time_per_mah = 0.03

        for drone_data in data_dict.get("drones", []):
            start_pos_list = drone_data.get("start_pos", [0.0, 0.0])
            drone = Drone(
                id=drone_data["id"],
                max_weight=drone_data["max_weight"],
                battery_capacity=drone_data["battery"],
                speed=drone_data["speed"],
                start_pos=tuple(start_pos_list),
                consumption_rate=drone_data.get("consumption_rate", default_consumption_rate),
                charge_time_per_mah=drone_data.get("charge_time_per_mah", default_charge_time_per_mah)
            )
            loaded_drones.append(drone)

        for delivery_data in data_dict.get("deliveries", []):
            pos_list = delivery_data.get("pos", [0.0, 0.0])
            time_window_list = delivery_data.get("time_window")
            if time_window_list:
                tw_start = sim_start_datetime_obj + timedelta(minutes=time_window_list[0])
                tw_end = sim_start_datetime_obj + timedelta(minutes=time_window_list[1])
                time_window = (tw_start.strftime("%H:%M"), tw_end.strftime("%H:%M"))
            else:
                time_window = None
            delivery = DeliveryPoint(
                id=delivery_data["id"],
                pos=tuple(pos_list),
                weight=delivery_data["weight"],
                priority=delivery_data["priority"],
                time_window=time_window
            )
            loaded_deliveries.append(delivery)

        for nfz_data in data_dict.get("no_fly_zones", []):
            coordinates_list_of_lists = nfz_data.get("coordinates", [])
            coordinates_tuples = [tuple(coord) for coord in coordinates_list_of_lists]
            active_time_input = nfz_data.get("active_time")
            nfz_active_time_str_tuple = None
            if active_time_input and isinstance(active_time_input[0], int):
                start_offset_minutes, end_offset_minutes = active_time_input
                nfz_start_dt = sim_start_datetime_obj + timedelta(minutes=start_offset_minutes)
                nfz_end_dt = sim_start_datetime_obj + timedelta(minutes=end_offset_minutes)
                nfz_active_time_str_tuple = (nfz_start_dt.strftime("%H:%M"), nfz_end_dt.strftime("%H:%M"))
            elif active_time_input and isinstance(active_time_input[0], str):
                nfz_active_time_str_tuple = tuple(active_time_input)
            nfz = NoFlyZone(
                id=nfz_data["id"],
                coordinates=coordinates_tuples,
                active_time=nfz_active_time_str_tuple
            )
            loaded_nfzs.append(nfz)
        
        self.drones = loaded_drones
        self.deliveries = loaded_deliveries
        self.no_fly_zones = loaded_nfzs
        self.deliveries_dict = {d.id: d for d in self.deliveries} 
        for dr in self.drones:
            dr.current_battery = dr.battery_capacity

    def run_simulation(self):

        self.total_deliveries_made = 0
        self.total_energy_consumed_mah = 0.0
        self.total_flight_distance_meters = 0.0
        self.failed_deliveries_time_window = 0
        self.failed_deliveries_battery_csp = 0
        self.failed_deliveries_nfz_csp = 0
        self.failed_deliveries_path_issue = 0
        self.failed_deliveries_battery_midway = 0
        self.failed_deliveries_battery_mid_step = 0
        self.failed_deliveries_path_incomplete = 0

        start_sim_pytime = pytime.time()
        self.current_sim_time_obj = parse_time(self.SIMULATION_START_TIME_STR[:-3])
        self.simulation_end_time_obj = parse_time(self.SIMULATION_END_TIME_STR[:-3])

        for d_obj in self.deliveries:
            d_obj.status = "pending"
            d_obj.is_assigned = False
            d_obj.assigned_drone_id = None

        self.drone_paths_history = {d.id: [] for d in self.drones}
        self.active_drone_segments = {}

        simulation_running = True
        print(f"\n--- Simülasyon Başlıyor ({self.SIMULATION_START_TIME_STR} - {self.SIMULATION_END_TIME_STR}) ---")

        while simulation_running and time_to_seconds(self.current_sim_time_obj) < time_to_seconds(self.simulation_end_time_obj):
            print(f"\n--- Simülasyon Zamanı: {self.current_sim_time_obj.strftime('%H:%M:%S')} ---")

            # 1. Dinamik Atama (CSP)
            assignable_drones = [d for d in self.drones if not d.is_busy]
            current_pending_deliveries_for_csp = [d for d_id, d in self.deliveries_dict.items() if d.status == "pending"]

            if assignable_drones and current_pending_deliveries_for_csp:
                # CSP çözümüne base_station_pos'u ilet
                assignments = solve_assignment_csp(assignable_drones, current_pending_deliveries_for_csp, self.no_fly_zones, self.current_sim_time_obj, self.BASE_STATION_POS)

                if assignments:
                    for assignment in assignments:
                        drone = next((d for d in self.drones if d.id == assignment['drone_id']), None)
                        delivery = self.deliveries_dict.get(assignment['delivery_id'])
                        path_info: PathInfo = assignment['path_info'] # Tip ipucu ekle

                        if drone and delivery and not drone.is_busy and delivery.status == "pending":
                            min_required_battery = drone.battery_capacity * self.DRONE_MIN_CHARGE_FOR_NEW_TASK_PERCENT
                            if drone.current_battery < min_required_battery and drone.current_pos != self.BASE_STATION_POS:
                                print(f"Drone {drone.id} ({drone.current_battery:.2f}mAh) yeterli şarjı olmadığı için görev atlayabilir.")
                                continue

                            print(f"Atama: Drone {drone.id} -> Teslimat {delivery.id} (Yol uzunluğu: {path_info.length:.2f}m)")
                            drone.assign_delivery(delivery.id, path_info.points)
                            delivery.status = "assigned"
                            delivery.is_assigned = True
                            delivery.assigned_drone_id = drone.id

                            self.active_drone_segments[drone.id] = [drone.current_pos]

            # 2. Drone Hareketleri ve Teslimat Simülasyonu
            for drone in self.drones:
                if not drone.is_busy:
                    if drone.id in self.active_drone_segments:
                        if len(self.active_drone_segments[drone.id]) > 1:
                            self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                        del self.active_drone_segments[drone.id]

                    # Şarj mantığı
                    if drone.current_battery < drone.battery_capacity * self.DRONE_CHARGE_THRESHOLD_PERCENT:
                        if drone.current_pos != self.BASE_STATION_POS:
                            pass
                        else:
                            charge_duration_seconds = drone.charge()
                    continue

                delivery = self.deliveries_dict.get(drone.current_delivery_id)
                if not delivery:
                    print(f"HATA: Drone {drone.id} için atanan teslimat ID {drone.current_delivery_id} bulunamadı. Görev iptal ediliyor.")
                    if drone.id in self.active_drone_segments:
                        if len(self.active_drone_segments[drone.id]) > 1: self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                        del self.active_drone_segments[drone.id]
                    drone.complete_delivery(drone.current_pos)
                    continue

                target_waypoint = delivery.pos
                if drone.path and drone.path[0] == drone.current_pos and len(drone.path) > 1: target_waypoint = drone.path[1]
                elif drone.path and drone.path[0] != drone.current_pos : target_waypoint = drone.path[0]
                elif not drone.path :
                    print(f"HATA: Drone {drone.id} için path boş, görev {delivery.id}. Mevcut konumda bitiriliyor.")
                    delivery.status = "failed_path_issue"; self.failed_deliveries_path_issue +=1
                    if drone.id in self.active_drone_segments:
                        if len(self.active_drone_segments[drone.id]) > 1: self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                        del self.active_drone_segments[drone.id]
                    drone.complete_delivery(drone.current_pos)
                    continue

                distance_to_waypoint = euclidean_distance(drone.current_pos, target_waypoint)
                if distance_to_waypoint < 0.01 : # Yol noktasından yeterince yakınsa
                     if target_waypoint == delivery.pos: # Teslimat noktasına ulaşıldı
                        actual_arrival_time = self.current_sim_time_obj # Mevcut simülasyon zamanı
                        if not delivery.is_within_time_window(actual_arrival_time) and delivery.status not in ["failed_time_window", "completed"]:
                             delivery.status = "failed_time_window"; self.failed_deliveries_time_window += 1

                        delivery.status = "completed" if delivery.status not in ["failed_time_window"] else delivery.status
                        if delivery.status == "completed": self.total_deliveries_made += 1

                        if drone.id in self.active_drone_segments:
                            if drone.current_pos not in self.active_drone_segments[drone.id]: self.active_drone_segments[drone.id].append(drone.current_pos)
                            if len(self.active_drone_segments[drone.id]) > 1: self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                            del self.active_drone_segments[drone.id]
                        drone.complete_delivery(delivery.pos)
                        continue
                     else: 
                        if drone.path: drone.path.pop(0)
                        if not drone.path and drone.current_pos != delivery.pos:
                           
                            delivery.status = "failed_path_incomplete"; self.failed_deliveries_path_incomplete += 1
                            if drone.id in self.active_drone_segments:
                                if drone.current_pos not in self.active_drone_segments[drone.id]: self.active_drone_segments[drone.id].append(drone.current_pos)
                                if len(self.active_drone_segments[drone.id]) > 1: self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                                del self.active_drone_segments[drone.id]
                            drone.complete_delivery(drone.current_pos)
                            continue
                        if drone.id in self.active_drone_segments and drone.current_pos not in self.active_drone_segments[drone.id]:
                            self.active_drone_segments[drone.id].append(drone.current_pos)
                        continue


                travel_distance_this_step = drone.speed * self.SIMULATION_STEP_SECONDS
                moved_this_step = False
                delivery_finalized_this_step = False

                if travel_distance_this_step >= distance_to_waypoint:
                    flight_time_to_waypoint = drone.calculate_flight_time(distance_to_waypoint)
                    energy_consumed = drone.calculate_battery_consumption(flight_time_to_waypoint)
                    if drone.current_battery >= energy_consumed:
                        drone.current_battery -= energy_consumed; self.total_energy_consumed_mah += energy_consumed
                        self.total_flight_distance_meters += distance_to_waypoint
                        drone.current_pos = target_waypoint; moved_this_step = True
                        if target_waypoint == delivery.pos: # Teslimat noktasına ulaşıldı
                            actual_arrival_time = add_seconds_to_time(self.current_sim_time_obj, flight_time_to_waypoint)
                            if not delivery.is_within_time_window(actual_arrival_time) and delivery.status not in ["failed_time_window", "completed"]:
                                delivery.status = "failed_time_window"; self.failed_deliveries_time_window += 1

                            if delivery.status in ["assigned", "pending"]: # Sadece zaten tamamlanmamışsa tamamla
                                delivery.status = "completed" if delivery.status not in ["failed_time_window"] else delivery.status
                            if delivery.status == "completed": self.total_deliveries_made += 1

                            drone.complete_delivery(delivery.pos); delivery_finalized_this_step = True
                        else: 
                            if drone.path: drone.path.pop(0)
                            if not drone.path and drone.current_pos != delivery.pos:
                                delivery.status = "failed_path_incomplete"; self.failed_deliveries_path_incomplete += 1
                                drone.complete_delivery(drone.current_pos); delivery_finalized_this_step = True
                    else: 
                        delivery.status = "failed_battery_midway"; self.failed_deliveries_battery_midway +=1
                        drone.complete_delivery(drone.current_pos); delivery_finalized_this_step = True
                else:
                    energy_consumed_this_step = drone.calculate_battery_consumption(self.SIMULATION_STEP_SECONDS)
                    if drone.current_battery >= energy_consumed_this_step:
                        drone.current_battery -= energy_consumed_this_step; self.total_energy_consumed_mah += energy_consumed_this_step
                        self.total_flight_distance_meters += travel_distance_this_step
                        dir_x = target_waypoint[0] - drone.current_pos[0]; dir_y = target_waypoint[1] - drone.current_pos[1]
                        norm_x = dir_x / distance_to_waypoint if distance_to_waypoint > 0 else 0
                        norm_y = dir_y / distance_to_waypoint if distance_to_waypoint > 0 else 0
                        drone.current_pos = (drone.current_pos[0] + norm_x * travel_distance_this_step, drone.current_pos[1] + norm_y * travel_distance_this_step)
                        moved_this_step = True
                    else:
                        delivery.status = "failed_battery_mid_step"; self.failed_deliveries_battery_mid_step +=1
                        drone.complete_delivery(drone.current_pos); delivery_finalized_this_step = True

                if moved_this_step and drone.id in self.active_drone_segments:
                     self.active_drone_segments[drone.id].append(drone.current_pos)

                if delivery_finalized_this_step and drone.id in self.active_drone_segments:
                    if drone.current_pos not in self.active_drone_segments[drone.id]:
                        self.active_drone_segments[drone.id].append(drone.current_pos)

                    if len(self.active_drone_segments[drone.id]) > 1:
                        self.drone_paths_history.setdefault(drone.id, []).append(list(self.active_drone_segments[drone.id]))
                    del self.active_drone_segments[drone.id]

            self.current_sim_time_obj = add_seconds_to_time(self.current_sim_time_obj, float(self.SIMULATION_STEP_SECONDS))
            if all(d.status not in ["pending", "assigned"] for d in self.deliveries_dict.values()):
                print("Tüm teslimatlar işlendi (tamamlandı veya başarısız oldu).")
                simulation_running = False

        # Simülasyon Sonu
        end_sim_pytime = pytime.time()
        execution_time_seconds = end_sim_pytime - start_sim_pytime

        print(f"\n--- Simülasyon Bitti ---")
        print(f"Simülasyon Süresi (oyun içi): {self.current_sim_time_obj.strftime('%H:%M:%S')}")
        print(f"Gerçek Çalışma Süresi: {execution_time_seconds:.2f} saniye")

        num_total_deliveries = len(self.deliveries)
        completed_percentage = (self.total_deliveries_made / num_total_deliveries) * 100 if num_total_deliveries > 0 else 0
        avg_energy_per_delivery = (self.total_energy_consumed_mah / self.total_deliveries_made) if self.total_deliveries_made > 0 else 0

        print(f"\n--- Performans Metrikleri ---")
        print(f"Toplam Teslimat Sayısı: {num_total_deliveries}")
        print(f"Başarıyla Tamamlanan Teslimat: {self.total_deliveries_made}")
        print(f"Tamamlanan Teslimat Yüzdesi: {completed_percentage:.2f}%")
        print(f"Toplam Enerji Tüketimi: {self.total_energy_consumed_mah:.2f} mAh")
        if self.total_deliveries_made > 0 : print(f"Teslimat Başına Ortalama Enerji: {avg_energy_per_delivery:.2f} mAh")
        print(f"Toplam Uçuş Mesafesi: {self.total_flight_distance_meters:.2f} m")

        failed_count = num_total_deliveries - self.total_deliveries_made
        print(f"Başarısız/İptal Edilen Teslimat: {failed_count}")
        if failed_count > 0:
            print(f"  - Zaman Penceresi İhlaliyle Başarısız: {self.failed_deliveries_time_window}")
            status_counts = {}
            for d_obj in self.deliveries_dict.values():
                status_counts[d_obj.status] = status_counts.get(d_obj.status, 0) + 1
            print(f"  - Teslimat Durumları Dağılımı: {status_counts}")


        results = {
            "completed_deliveries_count": self.total_deliveries_made,
            "completed_deliveries_percent": completed_percentage,
            "total_energy_consumption_mah": self.total_energy_consumed_mah,
            "avg_energy_consumption_per_delivery_mah": avg_energy_per_delivery,
            "total_flight_distance_m": self.total_flight_distance_meters,
            "execution_time_sec": execution_time_seconds,
            "final_drone_states": [str(d) for d in self.drones],
            "delivery_statuses": {d.id: d.status for d in self.deliveries_dict.values()},
            "drone_paths_history": self.drone_paths_history
        }
        return results