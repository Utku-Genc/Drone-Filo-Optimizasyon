from typing import Tuple, Optional
from datetime import datetime, time, timedelta

class DeliveryPoint:
    """
    Bir teslimat noktasını ve onunla ilişkili bilgileri temsil eder.
    """
    def __init__(self, id: int, pos: Tuple[float, float], weight: float, priority: int, time_window: Optional[Tuple[str, str]] = None):
        self.id = id
        self.pos = pos  # (x, y) koordinatları
        self.weight = weight  # kg
        self.priority = priority
        self.time_window = time_window  # (başlangıç_saati_str, bitiş_saati_str)
        self.status = "pending"  # Teslimat durumu: "pending", "in_progress", "completed", "failed"
        self.is_assigned = False
        self.assigned_drone_id: Optional[int] = None

    def is_within_time_window(self, current_time: datetime.time) -> bool:
        
        if self.time_window is None:
            return True  

        try:
            window_start = datetime.strptime(self.time_window[0], "%H:%M").time()
            window_end = datetime.strptime(self.time_window[1], "%H:%M").time()
        except ValueError:
            print(f"HATA: Teslimat {self.id} için geçersiz zaman penceresi formatı: {self.time_window}")
            return True 

        return window_start <= current_time <= window_end

    def __str__(self):
        return (f"Delivery(ID: {self.id}, Pos: {self.pos}, Weight: {self.weight}kg, "
                f"Priority: {self.priority}, TimeWindow: {self.time_window}, "
                f"Status: {self.status}, AssignedDrone: {self.assigned_drone_id})")

    def __repr__(self):
        return self.__str__()