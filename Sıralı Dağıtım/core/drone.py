from typing import Tuple, List, Optional
from datetime import datetime, time, timedelta

class Drone:
    """
    Bir dronun özelliklerini, durumunu ve davranışlarını temsil eder.
    """
    def __init__(self, id: int, max_weight: float, battery_capacity: float, speed: float, start_pos: Tuple[float, float], consumption_rate: float = 1.0, charge_time_per_mah: float = 0.03):
        self.id = id
        self.max_weight = max_weight  # kg
        self.battery_capacity = battery_capacity  # mAh
        self.current_battery = battery_capacity  # mAh
        self.speed = speed  # m/s
        self.current_pos = start_pos  # (x, y) koordinatları
        self.is_busy = False
        self.current_delivery_id: Optional[int] = None
        self.path: Optional[List[Tuple[float, float]]] = None  # Atanan görev için yol
        self.consumption_rate = consumption_rate # mAh/s/m 
        self.charge_time_per_mah = charge_time_per_mah # saniye/mAh

    def assign_delivery(self, delivery_id: int, path: List[Tuple[float, float]]):
        self.is_busy = True
        self.current_delivery_id = delivery_id
        self.path = path  # Atanan teslimat için yol
    def complete_delivery(self, final_pos: Tuple[float, float]):
        self.is_busy = False
        self.current_delivery_id = None
        self.path = None
        self.current_pos = final_pos # Teslimat sonrası konum güncellemesi

    def calculate_flight_time(self, distance: float) -> float:

        if self.speed <= 0:
            return float('inf')  
        return distance / self.speed

    def calculate_battery_consumption(self, flight_duration_seconds: float) -> float:
        # Uçuş süresine göre batarya tüketimini hesaplar.       
        # tüketim oranı * süre
        return self.consumption_rate * flight_duration_seconds

    def charge(self) -> float:
        charge_needed = self.battery_capacity - self.current_battery
        if charge_needed <= 0:
            return 0.0 

        charge_duration_seconds = charge_needed * self.charge_time_per_mah
        self.current_battery = self.battery_capacity
        return charge_duration_seconds

    def __str__(self):
        return (f"Drone(ID: {self.id}, MaxWeight: {self.max_weight}kg, "
                f"Battery: {self.current_battery:.2f}/{self.battery_capacity:.2f}mAh, Speed: {self.speed}m/s, "
                f"Pos: {self.current_pos}, Busy: {self.is_busy}, Task: {self.current_delivery_id})")

    def __repr__(self):
        return self.__str__()