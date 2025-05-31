from data.sample_data import drones, deliveries, no_fly_zones
from graph.graph_builder import build_graph
from astar.astar import a_star
from csp.csp import backtracking_search
from ga.genetic_algorithm import genetic_algorithm
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def print_graph(graph):
    for node, edges in graph.items():
        print(f"Node {node} connects to:")
        for dest, cost in edges:
            print(f"  -> {dest} with cost {cost:.2f}")
        print()

def visualize(drones, deliveries, no_fly_zones, assignment):
    fig, ax = plt.subplots(figsize=(12, 12))

    # No-fly zonelar
    for zone in no_fly_zones:
        polygon = patches.Polygon(zone.coordinates, closed=True, color='red', alpha=0.3)
        ax.add_patch(polygon)

    # Droneların başlangıç noktaları
    for drone in drones:
        x, y = drone.start_pos
        ax.scatter(x, y, color='green', s=100)
        ax.text(x+1, y, f'Drone {drone.id}', color='green', fontsize=12, weight='bold')

    # Teslimat noktaları
    for delivery in deliveries:
        x, y = delivery.pos
        weight = delivery.weight
        ax.scatter(x, y, color='blue', s=weight*40)
        ax.text(x+0.5, y, f'D{delivery.id}', color='blue')

    # Atamaya göre rotaları oluştur (drone_id -> teslimat listesi)
    drone_routes = {d.id: [] for d in drones}
    for delivery_id, drone_id in assignment.items():
        drone_routes[drone_id].append(delivery_id)

    # Droneların rotalarını çiz
    colors = ['green', 'purple', 'orange', 'brown', 'blue']
    for idx, (drone_id, route) in enumerate(drone_routes.items()):
        drone_start = next(d.start_pos for d in drones if d.id == drone_id)
        # Rotayı teslimat sırasına göre sırala veya olduğu gibi kullan
        points = [drone_start] + [next(d.pos for d in deliveries if d.id == del_id) for del_id in route]

        xs, ys = zip(*points)
        ax.plot(xs, ys, color=colors[idx % len(colors)], linewidth=2, label=f'Drone {drone_id} Route')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_title("Drone Rotası ve Teslimatları Görselleştirme")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)
    ax.legend()
    plt.show()

def main():
    graph = build_graph(drones, deliveries)
    print("Graph connections:")
    print_graph(graph)

    current_time = 0
    csp_solution = backtracking_search(drones, deliveries, no_fly_zones, current_time)
    print(f"CSP solution (delivery_id -> drone_id): {csp_solution}")

    ga_solution = genetic_algorithm(drones, deliveries, no_fly_zones, current_time)
    print(f"GA best assignment (delivery_id -> drone_id): {ga_solution}")

    start = f"D{drones[0].id}"
    goal = f"DP{deliveries[0].id}"

    path = a_star(start, goal, graph, drones, deliveries, no_fly_zones, current_time)
    if path:
        print(f"A* path from {start} to {goal}: {path}")
    else:
        print(f"No valid path found from {start} to {goal}.")

    # Görselleştirme için GA çözümünü kullan
    visualize(drones, deliveries, no_fly_zones, ga_solution)

if __name__ == "__main__":
    main()
