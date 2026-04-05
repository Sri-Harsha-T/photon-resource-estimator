import numpy as np
import warnings

SQUEEZING_HARDWARE_LIMIT_DB = 15.0 # physical ceiling for current squeezing devices, in dB.

# Hardware overhead model
PHOTONIC_OVERHEAD = {
    "squeezer_per_squeezing_op": 1,
    "beamsplitters_per_op": 1,
    "detector_per_mode" : 1,
    "ancilla_ratio" : 0.25, # 25% extra modes for error/routing
    "loss_overhead_factor" : 1.3, #30% overhead to account for optical loss
    "squeezing_db_default": 12, # realistic squeezing level in dB for overhead estimation
}

class SqueezingThresholdWarning(UserWarning):
    pass

class ResourceEstimator:
    def __init__(self, overhead_model=None, loss_rate=0.05, squeezing_db=12):
        self.model = overhead_model if overhead_model else PHOTONIC_OVERHEAD
        self.loss_rate = loss_rate
        self.squeezing_db = squeezing_db

    def estimate(self, gate_counts: dict) -> dict:
        """
        Estimate the hardware resources required to implement a given photonic quantum circuit, based on its gate counts and an overhead model.
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

        # Squeezing threshold warning
        squeezing_per_mode = self.squeezing_db # squeezing level per operation, in dB
        warnings_list = []
        if squeezing_per_mode > SQUEEZING_HARDWARE_LIMIT_DB:
            msg = (
                f"WARNING: Requested squeezing level of {squeezing_per_mode} dB exceeds the hardware limit of {SQUEEZING_HARDWARE_LIMIT_DB} dB. "
                "This circuit is NOT physically realizable on current devices and may lead to unphysical resource estimates. Consider reducing the squeezing level or using a more realistic overhead model."
            )
            warnings_list.append(msg)
            warnings.warn(msg, SqueezingThresholdWarning)
        
        total_squeezing_per_mode = squeezing_budget_db / modes if modes > 0 else 0
        if total_squeezing_per_mode > SQUEEZING_HARDWARE_LIMIT_DB:
            msg = (
                f"WARNING: Total squeezing per mode of {total_squeezing_per_mode:.2f} dB exceeds the hardware limit of {SQUEEZING_HARDWARE_LIMIT_DB} dB. "
                "This circuit is NOT physically realizable on current devices and may lead to unphysical resource estimates. Consider reducing the squeezing level, optimizing the circuit to use fewer squeezing operations, or using a more realistic overhead model."
            )
            warnings_list.append(msg)
            warnings.warn(msg, SqueezingThresholdWarning)

        return {
            "squeezed_sources": squeezed_sources,
            "beamsplitters": beamsplitters,
            "detectors": detectors,
            "total_optical_modes": total_modes,
            "ancilla_modes": ancilla_modes,
            "circuit_depth": depth,
            "squeezing_budget_db": squeezing_budget_db,
            "squeezing_per_mode_db": squeezing_per_mode,
            "loss_overhead_factor": loss_overhead,
            "hardware_warnings": warnings_list,
        }
