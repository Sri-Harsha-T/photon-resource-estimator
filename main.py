import pennylane as qml
from estimator.circuit_analyzer import CircuitAnalyzer
from estimator.resource_engine import ResourceEstimator
from estimator.backends import BACKENDS
from estimator.report import print_report
# import strawberryfields as sf

def main():
    print("Hello from photonic-resource-estimator!")
    # Example usage with a simple GBS circuit

    def example_circuit():
        qml.Squeezing(0.5, 0, wires=0)
        qml.Squeezing(0.5, 0, wires=1)
        qml.Beamsplitter(0.78, 0, wires=[0,1])
        qml.Beamsplitter(0.78, 0, wires=[2,3])
        qml.Squeezing(0.3, 0, wires=2)
        # return qml.probs(wires=[0,1,2,3])
        return qml.expval(qml.NumberOperator(0))
    
    for backend_name, overhead_model in BACKENDS.items():
        analyzer = CircuitAnalyzer(example_circuit, n_wires=4)
        gate_counts = analyzer.analyze()

        estimator = ResourceEstimator(overhead_model=overhead_model)
        resources = estimator.estimate(gate_counts)

        print_report(backend_name, gate_counts, resources)

    dev = qml.device("default.gaussian", wires=4)

    # @qml.qnode(dev)
    # def runnable_example_circuit():
    #     qml.Squeezing(0.5, 0, wires=0)
    #     qml.Squeezing(0.5, 0, wires=1)
    #     qml.Beamsplitter(0.78, 0, wires=[0,1])
    #     qml.Beamsplitter(0.78, 0, wires=[2,3])
    #     qml.Squeezing(0.3, 0, wires=2)
    #     return qml.expval(qml.NumberOperator(0))
    
    # print("Running the example circuit on a Pennylane Gaussian backend...")
    # result = runnable_example_circuit()
    # print(f"Mean photon number on wire 0: {result}")

    runnable = qml.QNode(example_circuit, dev)
    print("Mean photon number on wire 0:", runnable())

    runnable()

    tape = qml.workflow.construct_tape(runnable)()
    # tape = result.tape

    gate_counts = {
        "squeezing_ops" : sum(1 for op in tape.operations if "Squeezing" in op.name),
        "beamsplitter_ops" : sum(1 for op in tape.operations if "Beamsplitter" in op.name),
        "rotation_ops" : sum(1 for op in tape.operations if "Rotation" in op.name),
        "displacement_ops" : sum(1 for op in tape.operations if "Displacement" in op.name),
        "measurement_ops" : len(tape.measurements),
        "total_modes" : tape.num_wires,
        "circuit_depth" : CircuitAnalyzer(example_circuit, n_wires=4)._estimate_depth(tape),
    }

    resources = ResourceEstimator(overhead_model=BACKENDS["gbs"]).estimate(gate_counts)
    print_report("gbs", gate_counts, resources)




if __name__ == "__main__":
    main()
