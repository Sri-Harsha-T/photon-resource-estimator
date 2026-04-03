

def print_report(backend: str, gate_counts: dict, resources: dict):
    print(f"\n{'='*60}")
    print(f"Resource estimation for {backend} backend:")
    print(f"{'-'*60}")
    print(f"    Circuit depth          : {gate_counts['circuit_depth']} layers")
    print(f"    Optical modes          : {resources['total_optical_modes']} ({resources['ancilla_modes']} ancilla modes)")
    print(f"    Squeezed sources       : {resources['squeezed_sources']}")
    print(f"    Beamsplitters          : {resources['beamsplitters']}")
    print(f"    Detectors              : {resources['detectors']}")
    print(f"    Squeezing budget       : {resources['squeezing_budget_db']} dB total")
    print(f"    Loss overhead factor   : {resources['loss_overhead_factor']:.2f}x")
    print(f"{'='*60}\n")

