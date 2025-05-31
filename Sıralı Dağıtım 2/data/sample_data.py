from models.drone import Drone
from models.delivery import DeliveryPoint
from models.noflyzone import NoFlyZone

drones = [
    Drone(1, 4.0, 12000, 8.0, (10, 10)),
    Drone(2, 3.5, 10000, 10.0, (20, 30)),
    Drone(3, 5.0, 15000, 7.0, (50, 50)),
    Drone(4, 2.0, 8000, 12.0, (80, 20)),
    Drone(5, 6.0, 20000, 5.0, (40, 70)),
]

deliveries = [
    DeliveryPoint(1, (15, 25), 1.5, 3, (0, 60)),
    DeliveryPoint(2, (30, 40), 2.0, 5, (0, 30)),
    DeliveryPoint(3, (70, 80), 3.0, 2, (20, 80)),
    DeliveryPoint(4, (90, 10), 1.0, 4, (10, 40)),
    DeliveryPoint(5, (45, 60), 4.0, 1, (30, 90)),
    DeliveryPoint(6, (25, 15), 2.5, 3, (0, 50)),
    DeliveryPoint(7, (60, 30), 1.0, 5, (5, 25)),
    DeliveryPoint(8, (85, 90), 3.5, 2, (40, 100)),
    DeliveryPoint(9, (10, 80), 2.0, 4, (15, 45)),
    DeliveryPoint(10, (95, 50), 1.5, 3, (0, 60)),
    DeliveryPoint(11, (55, 20), 0.5, 5, (0, 20)),
    DeliveryPoint(12, (35, 75), 2.0, 1, (50, 120)),
    DeliveryPoint(13, (75, 40), 3.0, 3, (10, 50)),
    DeliveryPoint(14, (20, 90), 1.5, 4, (30, 70)),
    DeliveryPoint(15, (65, 65), 4.5, 2, (25, 75)),
    DeliveryPoint(16, (40, 10), 2.0, 5, (0, 30)),
    DeliveryPoint(17, (5, 50), 1.0, 3, (15, 55)),
    DeliveryPoint(18, (50, 85), 3.0, 1, (60, 100)),
    DeliveryPoint(19, (80, 70), 2.5, 4, (20, 60)),
    DeliveryPoint(20, (30, 55), 1.5, 2, (40, 80)),
]

no_fly_zones = [
    NoFlyZone(1, [(40, 30), (60, 30), (60, 50), (40, 50)], (0, 120)),
    NoFlyZone(2, [(70, 10), (90, 10), (90, 30), (70, 30)], (30, 90)),
    NoFlyZone(3, [(10, 60), (30, 60), (30, 80), (10, 80)], (0, 60)),
]
