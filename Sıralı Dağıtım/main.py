from simulation.simulation_manager import SimulationManager
from simulation.visualizer import plot_simulation_results
from data.sample_data import SAMPLE_SIMULATION_DATA 

if __name__ == "__main__":
    print("\n" + "*"*10 + " Örnek Veri Seti ile Test " + "*"*10)

    sim_manager = SimulationManager()

    # Veriyi yükle
    sim_manager.load_data_from_dict(SAMPLE_SIMULATION_DATA)

    print(f"Yüklenen Drone Sayısı: {len(sim_manager.drones)}")
    print(f"Yüklenen Teslimat Sayısı: {len(sim_manager.deliveries)}")
    print(f"Yüklenen NFZ Sayısı: {len(sim_manager.no_fly_zones)}")

    # Simülasyonu çalıştır
    results_custom = sim_manager.run_simulation()

    # Sonuçları yazdır
    print(f"\n--- Örnek Veri Seti Sonuçları ---")
    for key, value in results_custom.items():
        if key not in ["final_drone_states", "delivery_statuses", "drone_paths_history"]:
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').capitalize()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').capitalize()}: {value}")
    
    # Görselleştirme
    if results_custom:
        plot_simulation_results(
            sim_manager.drones, # Simülasyon yöneticisindeki drone listesini kullan
            sim_manager.deliveries, # Simülasyon yöneticisindeki teslimat listesini kullan
            sim_manager.no_fly_zones,
            results_custom["drone_paths_history"],
            sim_manager.BASE_STATION_POS
        )