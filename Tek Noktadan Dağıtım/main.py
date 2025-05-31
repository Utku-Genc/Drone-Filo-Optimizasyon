import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from data.sample_data import drones, deliveries, no_fly_zones
from graph.graph_builder import build_graph
from astar.astar import a_star
from csp.csp import backtracking_search
from ga.genetic_algorithm import genetic_algorithm

def get_priority_queue(deliveries):
    # (-priority, delivery_id, delivery_obj) ile heap oluştur (min-heap)
    heap = [(-d.priority, d.id, d) for d in deliveries]
    heapq.heapify(heap)
    return heap

def print_graph(graph):
    for node, edges in graph.items():
        print(f"Node {node} connects to:")
        for dest, cost in edges:
            print(f"  -> {dest} with cost {cost:.2f}")
        print()

def visualize(drones, deliveries, no_fly_zones, assignment):
    fig, ax = plt.subplots(figsize=(10,10))

    # No-Fly Zone'ları çiz
    for zone in no_fly_zones:
        polygon = patches.Polygon(zone.coordinates, closed=True, color='red', alpha=0.3)
        ax.add_patch(polygon)
        ax.text(
            sum(x for x, y in zone.coordinates) / len(zone.coordinates),
            sum(y for x, y in zone.coordinates) / len(zone.coordinates),
            f'NFZ {zone.id}', color='red', fontsize=12, weight='bold'
        )

    # Droneların başlangıç noktaları
    for d in drones:
        ax.scatter(*d.start_pos, c='blue', marker='s', s=100, label=f"Drone {d.id}")
        ax.text(d.start_pos[0], d.start_pos[1], f"D{d.id}", fontsize=9, weight='bold', color='blue')

    # Teslimat noktaları ve atamalar
    colors = ['green', 'purple', 'orange', 'brown', 'cyan']  # Drone'lar için renkler
    drone_color_map = {d.id: colors[i % len(colors)] for i, d in enumerate(drones)}

    for delivery in deliveries:
        assigned_drone_id = assignment.get(delivery.id)
        c = drone_color_map.get(assigned_drone_id, 'gray')
        ax.scatter(*delivery.pos, c=c, marker='o', s=60)
        ax.text(delivery.pos[0], delivery.pos[1], f"P{delivery.id}", fontsize=8, color=c)

        # Dronenin start_pos ile teslimat arasında çizgi (rota)
        if assigned_drone_id:
            drone_start = next(d.start_pos for d in drones if d.id == assigned_drone_id)
            ax.plot([drone_start[0], delivery.pos[0]], [drone_start[1], delivery.pos[1]], c=c, linestyle='--', alpha=0.7)

    ax.set_xlim(0, 110)
    ax.set_ylim(0, 110)
    ax.set_title("Drone Rotaları, Teslimatlar ve No-Fly Zones")
    ax.legend()
    plt.grid(True)
    plt.show()

def main():
    # Komşuluk listesi graph oluştur
    graph = build_graph(drones, deliveries)
    print("Graph connections:")
    print_graph(graph)

    current_time = 0

    # CSP çözüm (delivery_id -> drone_id)
    csp_solution = backtracking_search(drones, deliveries, no_fly_zones, current_time)
    print(f"CSP solution (delivery_id -> drone_id): {csp_solution}")

    # GA çözüm (delivery_id -> drone_id)
    ga_solution = genetic_algorithm(drones, deliveries, no_fly_zones, current_time)
    print(f"GA best assignment (delivery_id -> drone_id): {ga_solution}")

    # Min-Heap ile öncelikli teslimatlar (örnek: ilk 3 acil teslimat)
    delivery_pq = get_priority_queue(deliveries)
    print("Top 3 acil teslimatlar (priority, delivery_id):")
    for _ in range(3):
        if delivery_pq:
            priority, _, delivery = heapq.heappop(delivery_pq)
            print(f"Delivery {delivery.id} öncelik {-priority}")

    # A* ile rota örneği: İlk drone ve ilk teslimat
    start = f"D{drones[0].id}"
    goal = f"DP{deliveries[0].id}"
    path = a_star(start, goal, graph, drones, deliveries, no_fly_zones, current_time)
    if path:
        print(f"A* path from {start} to {goal}: {path}")
    else:
        print(f"No valid path found from {start} to {goal}.")

    # Görselleştir (GA çözümünü kullanarak)
    visualize(drones, deliveries, no_fly_zones, ga_solution)

if __name__ == "__main__":
    main()
