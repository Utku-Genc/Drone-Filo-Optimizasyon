import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Tuple
from core.drone import Drone
from core.delivery_point import DeliveryPoint
from core.no_fly_zone import NoFlyZone

def plot_simulation_results(
    drones_initial: List[Drone], 
    deliveries: List[DeliveryPoint],
    no_fly_zones: List[NoFlyZone],
    drone_paths_history: Dict[int, List[List[Tuple[float, float]]]],
    base_pos: Tuple[float, float],
):
    fig, ax = plt.subplots(figsize=(14, 12))

    # No-Fly Zones
    for nfz in no_fly_zones:
        color = 'lightcoral'
        polygon = patches.Polygon(nfz.coordinates, closed=True, facecolor=color, alpha=0.4, edgecolor='red', linewidth=1)
        ax.add_patch(polygon)
        center_x = sum(p[0] for p in nfz.coordinates) / len(nfz.coordinates)
        center_y = sum(p[1] for p in nfz.coordinates) / len(nfz.coordinates)
        ax.text(center_x, center_y, f"NFZ {nfz.id}", ha='center', va='center', fontsize=7, color='darkred', bbox=dict(boxstyle="round,pad=0.3", fc="wheat", alpha=0.5))

    # Teslimat Noktaları
    status_colors_markers = {
        "pending": ('blue', 's', 'Pending'),
        "assigned": ('orange', 'D', 'Assigned'),
        "completed": ('green', 'o', 'Completed'),
        "failed_time_window": ('red', 'x', 'Failed (Time)'),
        "failed_nfz": ('maroon', 'x', 'Failed (NFZ)'),
        "failed_battery": ('darkred', 'X', 'Failed (Battery CSP)'),
        "failed_path_issue": ('purple', '*', 'Failed (Path Issue)'),
        "failed_battery_midway": ('black', 'P', 'Failed (Battery Midway)'),
        "failed_battery_mid_step": ('dimgray', 'P', 'Failed (Battery Step)'),
        "failed_path_incomplete": ('brown', '*', 'Failed (Path Incomplete)'),
    }
    plotted_delivery_labels = set()
    for delivery in deliveries:
        x, y = delivery.pos
        color, marker, status_label = status_colors_markers.get(delivery.status, ('gray', '.', 'Unknown Status'))

        legend_label = None
        if status_label not in plotted_delivery_labels:
            legend_label = status_label
            plotted_delivery_labels.add(status_label)

        ax.scatter(x, y, color=color, marker=marker, s=60, label=legend_label, zorder=5, edgecolors='black', linewidths=0.5)
        ax.text(x + 1, y + 1, str(delivery.id), fontsize=7, zorder=6)

    ax.scatter(base_pos[0], base_pos[1], color='black', marker='H', s=150, label='Base Station', zorder=6, edgecolors='white')

    for drone_init_state in drones_initial:
        if drone_init_state.current_pos != base_pos:
             ax.scatter(drone_init_state.current_pos[0], drone_init_state.current_pos[1],
                        color='cyan', marker='^', s=80, label=f'Drone Start Pos' if drone_init_state.id==drones_initial[0].id else None,
                        zorder=4, edgecolors='blue')

    # Drone Yolları Renk
    path_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'orange', 'purple', 'brown', 'pink']
    drone_id_to_label_plotted = {} 
    for i, drone_id in enumerate(drone_paths_history.keys()):
        paths = drone_paths_history[drone_id]
        drone_color = path_colors[drone_id % len(path_colors)]

        label_for_this_drone = None
        if drone_id not in drone_id_to_label_plotted:
            label_for_this_drone = f'Drone {drone_id} Path'
            drone_id_to_label_plotted[drone_id] = True

        for path_segment in paths:
            if len(path_segment) > 1:
                xs, ys = zip(*path_segment)
                ax.plot(xs, ys, linestyle='-', marker='.', markersize=4, color=drone_color, alpha=0.6,
                        label=label_for_this_drone if path_segment == paths[0] else None, 
                        linewidth=1.5)

    all_x = [p[0] for d in deliveries for p in [d.pos]] + [base_pos[0]]
    all_y = [p[1] for d in deliveries for p in [d.pos]] + [base_pos[1]]
    for drone_init in drones_initial:
        all_x.append(drone_init.current_pos[0])
        all_y.append(drone_init.current_pos[1]) 
    for paths in drone_paths_history.values():
        for segment in paths:
            for p in segment: all_x.append(p[0]); all_y.append(p[1])
    for nfz in no_fly_zones:
        for p in nfz.coordinates: all_x.append(p[0]); all_y.append(p[1])

    if not all_x or not all_y:
        all_x.extend([0,10]); all_y.extend([0,10])

    padding = 15
    ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
    ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
    ax.set_xlabel("X Koordinatı (m)")
    ax.set_ylabel("Y Koordinatı (m)")
    ax.set_title("Drone Filo Simülasyonu Görselleştirmesi", fontsize=16)

    # Legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0., fontsize=9)

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_aspect('equal', adjustable='box')
    plt.subplots_adjust(right=0.75) #
    plt.show()