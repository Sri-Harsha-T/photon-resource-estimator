import csv
import os
from datetime import datetime

def export_to_csv(gate_counts : dict, all_resources: dict, sweep_results: list[dict] = None, output_dir: str = "outputs"):
    """
    Export the resource estimation results to a CSV file, including gate counts, estimated resources, and optional sweep results.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resource_estimation_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    main_fields = [
        "backend", "squeezed_sources", "beamsplitters", "detectors",
        "total_optical_modes", "ancilla_modes", "circuit_depth",
        "squeezing_budget_db", "squeezing_per_mode_db", "loss_overhead_factor", "hardware_warnings"
    ]

    with open(filepath, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=main_fields)
        writer.writeheader()
        for backend, resources in all_resources.items():
            row = {"backend": backend}
            row.update({k: resources.get(k, "") for k in main_fields[1:]})
            row["hardware_warnings"] = "; ".join(resources.get("hardware_warnings", [])) if resources.get("hardware_warnings") else ""
            writer.writerow(row)

    print(f"Resource estimation results exported to {filepath}")

    if sweep_results:
        sweep_path = os.path.join(output_dir, f"noise_sweep_{timestamp}.csv")
        sweep_fields = ["loss_rate", "backend", "detectors", "squeezed_sources", "loss_overhead"]
        with open(sweep_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sweep_fields)
            writer.writeheader()
            for result in sweep_results:
                row = {k: result.get(k, "") for k in sweep_fields}
                writer.writerow(row)
        print(f"Noise sweep results exported to {sweep_path}")