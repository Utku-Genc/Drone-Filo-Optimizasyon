from typing import List, Tuple, Optional
from datetime import datetime, time, timedelta

try:
    from shapely.geometry import Polygon, Point
    SHAPELY_AVAILABLE = True
except ImportError:
    print("Shapely kütüphanesi bulunamadı. NoFlyZone için temel geometrik kontroller kullanılacak.")
    SHAPELY_AVAILABLE = False

class NoFlyZone:
    def __init__(self, id: int, coordinates: List[Tuple[float, float]], active_time: Optional[Tuple[str, str]] = None):
        self.id = id
        self.coordinates = coordinates  # Köşe koordinatlarının listesi [(x1, y1), (x2, y2), ...]
        self.active_time = active_time  # (başlangıç_saati_str, bitiş_saati_str)

        if SHAPELY_AVAILABLE:
            self.polygon = Polygon(self.coordinates)
        else:
            self.polygon = None # Shapely yoksa None

    def is_active(self, current_time: datetime.time) -> bool:

        if self.active_time is None:
            return True  

        try:
            active_start = datetime.strptime(self.active_time[0], "%H:%M").time()
            active_end = datetime.strptime(self.active_time[1], "%H:%M").time()
        except ValueError:
            print(f"HATA: NFZ {self.id} için geçersiz zaman penceresi formatı: {self.active_time}")
            return True 
        return active_start <= current_time <= active_end

    def contains_point(self, point: Tuple[float, float]) -> bool:

        if not SHAPELY_AVAILABLE or self.polygon is None:
            # Basit Ray Casting algoritması (Shapely yoksa)
            # Kaynak: https://wrf.ecse.rpi.edu//Teaching/graphics-f2010/lectures/L07_Polygons.pdf
            x, y = point
            n = len(self.coordinates)
            inside = False
            p1x, p1y = self.coordinates[0]
            for i in range(n + 1):
                p2x, p2y = self.coordinates[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            return inside
        else:
            return self.polygon.contains(Point(point))

    def intersects_segment(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:

        # Bir doğru parçasının uçuşa yasak bölge ile kesişip kesişmediğini kontrol eder.

        if not SHAPELY_AVAILABLE or self.polygon is None:
            return self.contains_point(p1) or self.contains_point(p2)
        else:
            from shapely.geometry import LineString
            line = LineString([p1, p2])
            return self.polygon.intersects(line)

    def __str__(self):
        return (f"NoFlyZone(ID: {self.id}, Coords: {self.coordinates}, ActiveTime: {self.active_time})")