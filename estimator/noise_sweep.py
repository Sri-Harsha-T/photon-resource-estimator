import numpy as np
from estimator.resource_engine import ResourceEstimator
from estimator.backends import BACKENDS

def sweep_loss_rate(gate_counts : dict, loss_range = (0.01, 0.15), steps = 15, backend="gbs") -> list[dict]:
    """
    Sweep optical loss rate and record how physical resources scale.
    Returns a list of resource estimates at different loss rates.
    """
    model = BACKENDS[backend]
    results = []
    for loss_rate in np.linspace(*loss_range, steps):
        estimator = ResourceEstimator(overhead_model=model, loss_rate=loss_rate)
        resources = estimator.estimate(gate_counts)
        resources["loss_rate"] = loss_rate
        results.append({
            "loss_rate": loss_rate,
            "detectors": resources["detectors"],
            "squeezed_sources": resources["squeezed_sources"],
            "loss_overhead": resources["loss_overhead_factor"],
            "backend": backend,
        })
    return results

def print_sweep(results: list[dict]):
    print(f"\n{'Loss Rate':>10} | {'Detectors':>10} | {'Squeezed Sources':>12} | {'Loss Overhead':>14} | {'Backend':>10}")
    print("-" * 70)
    for res in results:
        print(f"{res['loss_rate']*100:9.2f}% | {res['detectors']:10d} | {res['squeezed_sources']:12d} | {res['loss_overhead']:14.2f} | {res['backend']:>10}")
