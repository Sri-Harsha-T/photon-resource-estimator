import numpy as np

# Hardware overhead model
PHOTONIC_OVERHEAD = {
    "squeezer_per_squeezing_op": 1,
    "beamsplitters_per_op": 1,
    "detector_per_mode" : 1,
    "ancilla_ratio" : 0.25, # 25% extra modes for error/routing
    "loss_overhead_factor" : 1.3, #30% overhead to account for optical loss
    "squeezing_db_default": 12, # realistic squeezing level in dB for overhead estimation
}

class ResourceEstimator:
    def __init__(self, overhead_model=None, loss_rate=0.05, squeezing_db=12):
        self.model = overhead_model if overhead_model else PHOTONIC_OVERHEAD
        self.loss_rate = loss_rate
        self.squeezing_db = squeezing_db

    def estimate(self, gate_counts: dict) -> dict:
        """
        
        """

        m = self.model
        modes = gate_counts.get("total_modes", 0)
        ancilla_modes = int(np.ceil(modes * m["ancilla_ratio"]))
        total_modes = modes + ancilla_modes

        # Loss overhead: more layers = more loss = more redundancy required
        depth = gate_counts.get("circuit_depth", 0)
        loss_overhead = 1 + self.loss_rate * depth

        squeezed_sources = int( np.ceil(gate_counts.get("squeezing_ops", 0) * m["squeezer_per_squeezing_op"] * loss_overhead) )
        beamsplitters = int( np.ceil(gate_counts.get("beamsplitter_ops", 0) * m["beamsplitters_per_op"]) )
        detectors = int( np.ceil(total_modes * m["detector_per_mode"] * loss_overhead) )

        # Squeezing budget: sum over all ops, in dB
        squeezing_budget_db = gate_counts.get("squeezing_ops", 0) * self.squeezing_db

        return {
            "squeezed_sources": squeezed_sources,
            "beamsplitters": beamsplitters,
            "detectors": detectors,
            "total_optical_modes": total_modes,
            "ancilla_modes": ancilla_modes,
            "circuit_depth": depth,
            "squeezing_budget_db": squeezing_budget_db,
            "loss_overhead_factor": loss_overhead,
        }
