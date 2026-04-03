import pennylane as qml
from pennylane.ops import Squeezing, Beamsplitter, Rotation

class CircuitAnalyzer:
    """Parses a Pennylane photonic circuit tape and extracts raw gate counts"""

    def __init__(self, circuit_fn, n_wires):
        self.circuit_fn = circuit_fn
        self.n_wires = n_wires

    def get_tape(self, *args):
        """Execute the circuite and grab its tape for inspection"""
        return qml.tape.make_qscript(self.circuit_fn)(*args)

        tape = qml.tape.make_qscript(self.circuit_fn)(*args)
        return tape
    
    def analyze(self, *args):

        tape = self.get_tape(*args)
        counts = {
            "squeezing_ops": 0,
            "beamsplitter_ops": 0,
            "rotation_ops": 0,
            "displacement_ops": 0,
            "measurement_ops": len(tape.measurements),
            "total_modes" : tape.num_wires,
            "circuit_depth" : self._estimate_depth(tape),
        }
        for op in tape.operations:
            name = op.name
            if "Squeezing" in name:
                counts["squeezing_ops"] += 1
            if "Beamsplitter" in name:
                counts["beamsplitter_ops"] += 1
            if "Rotation" in name:
                counts["rotation_ops"] += 1
            if "Displacement" in name:
                counts["displacement_ops"] += 1
        return counts
    
    def _estimate_depth(self, tape):
        """Estimate circuite depth via layer counting on the tape"""
        mode_last_used = {}
        depth = 0
        for op in tape.operations:
            layer = max((mode_last_used.get(w, 0) for w in op.wires), default=0) + 1
            for w in op.wires:
                mode_last_used[w] = layer
            depth = max(depth, layer)
        return depth