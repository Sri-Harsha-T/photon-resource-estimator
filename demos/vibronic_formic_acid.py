"""
Photonic Resource Estimation: GBS Circuit Resource Estimation Engine for Vibronic Spectra of Formic Acid
========================================================================================================
Demo algorithm : Molecular Vibronic Spectra of Formic Acid via Gaussian Boson Sampling (GBS)
References:
- [1] Huh, J., Guerreschi, G. G., Peropadre, B., McClean, J., & Aspuru-Guzik, A. (2015). "Boson sampling for molecular vibronic spectra."
      Nature Photonics, 9(9), 615-620. doi: 10.1038/nphoton.2015.153
- [2] Bromley et al. (2020). "Applications of Near-Term Photonic Quantum Computers: Software and Algorithms." arXiv:1912.07634 [quant-ph].
- [3] Hamilton et al. (2017). "Gaussian Boson Sampling." Physical Review Letters, 119(17), 170501. doi: 10.1103/PhysRevLett.119.170501
- [4] Killoran et al. (2019). "Strawberry Fields: A Software Platform for Photonic Quantum Computing." Quantum, 3, 129. doi: 10.22331/q-2019-03-11-129
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pennylane as qml

from estimator.circuit_analyzer import CircuitAnalyzer
from estimator.resource_engine import ResourceEstimator
from estimator.backends import BACKENDS
from estimator.report import print_report
from estimator.noise_sweep import sweep_loss_rate, print_sweep
from estimator.exporter import export_to_csv

# Formic acid GBS parameters from Huh et al. (2015). Ground state vibrational frequencies (in cm^-1) and Duschinsky matrix.

w = np.array([3462.06, 1883.41, 1497.46, 1258.24, 1097.89, 626.82, 504.17])

# Excited state vibrational frequencies (in cm^-1)
w_prime = np.array([3113.85, 1852.13, 1374.91, 1189.35, 1009.87, 621.36, 450.78])

# Duschinsky matrix (7x7): captures how normal modes transform between ground and excited states
D = np.array([
    [ 0.9596,  0.2577, -0.0459, 0.0415, -0.0101, 0.0023, -0.0050],
    [-0.2448,  0.8877,  0.3204, -0.1864,  0.0548, -0.0168,  0.0193],
    [ 0.0681, -0.3580,  0.8732, -0.2795,  0.1388, -0.0302,  0.0420],
    [-0.0317,  0.1489, -0.3580,  0.8704, -0.2969,  0.0842, -0.0626],
    [ 0.0074, -0.0561,  0.1569, -0.3636,  0.8674, -0.2882,  0.1524],
    [-0.0021,  0.0235, -0.0784,  0.2005, -0.3798,  0.8710, -0.2440],
    [ 0.0027, -0.0192,  0.0474, -0.1098,  0.2297, -0.3706,  0.9000],
])

# displacement vector (7x1): captures how the equilibrium positions of the normal modes shift between ground and excited states
delta = np.array([0.2254, 0.1782, 0.0680, 0.0486, 0.0232, 0.0451, 0.0538])

N_MODES = len(w) # number of vibrational modes

def compute_gbs_params(w, w_prime, D, delta, T=0):
    """
    Compute GBS squeezing and interferometer parameters from molecular vibronic data.
    Implements the Doktorov operator decomposition (Huh et al. 2015, eq. 4).

    Returns : 
    r_single : single-mode squeezing parameters (shape : N)
    t_two : two-mode squeezing parameters (shape : N) - from thermal state at T
    U1, U2 : interferometer unitaries (shape : N x N each)
    alpha : displacement parameters (shape : N)
    """

    # Frequency ratio matrices
    Omega = np.diag(np.sqrt(w))
    Omega_prime = np.diag(np.sqrt(w_prime))

    # Doktorov J matrix : J = Omega^{1/2} D Omega'^{-1/2}
    J = Omega @ D @ np.linalg.inv(Omega_prime)

    # Singular value decomposition of J : J = U1 @ Sigma @ U2^T gives the interferometer unitaries and single-mode squeezing parameters
    U2, s, U1h = np.linalg.svd(J)
    U1 = U1h.conj().T

    r_single = np.log(s) # single-mode squeezing parameters in natural units

    # Two-mode squeezing parameters from thermal population at temperature T 
    if T == 0:
        t_two = np.zeros(N_MODES) # no thermal population at zero temperature
    else:
        kB_T = 0.695 * T # Boltzmann constant in cm^-1/K times temperature in K gives thermal energy in cm^-1
        n_thermal = 1.0/(np.exp(w / kB_T) - 1) # thermal population of each mode
        t_two = 0.5 * np.log(n_thermal + 1) # two-mode squeezing parameters in natural units

    # Displacement parameters 
    d = np.sqrt(2) * Omega @ delta # convert from dimensionless displacement to physical units
    alpha = U2.conj().T @ d / 2 # transform displacement into the interferometer basis

    return r_single, t_two, U1, U2, alpha

def build_vibronic_circuit(r_single, t_two, U1, U2, alpha):
    """
    Build a Pennylane quantum circuit that implements the GBS state preparation for molecular vibronic spectra, based on the computed parameters.

    Circuit structure (Doktorov decomposition):
    1. Two-mode squeezing (modes 0..N-1 paired with ancilla modes N..2N-1) for thermal state preparation
    2. Interferometer U1 (first N modes)
    3. Single-mode squeezing (modes 0..N-1)
    4. Interferometer U2 
    5. Displacements

    Total modes : N vibrational modes + N ancilla modes for thermal state = 2N modes
    """
    N = len(r_single)

    def circuit():
        
        # Step 1 : Two-mode squeezing for thermal state preparation - pairs mode i with ancilla mode N+i
        for i in range(N):
            if abs(t_two[i]) > 1e-8:
                qml.TwoModeSqueezing(t_two[i], 0, wires=[i, N+i])
            
        # Step 2 : Interferometer U1 on the first N modes
        qml.InterferometerUnitary(U1, wires=list(range(N)))

        # Step 3 : Single-mode squeezing on the first N modes
        for i in range(N):
            if abs(r_single[i]) > 1e-8:
                qml.Squeezing(r_single[i], 0, wires=i)
        # Step 4 : Interferometer U2 on the first N modes
        qml.InterferometerUnitary(U2, wires=list(range(N)))
        # Step 5 : Displacements on the first N modes
        for i in range(N):
            qml.Displacement(np.abs(alpha[i]), np.angle(alpha[i]), wires=i)
        
        return qml.expval(qml.NumberOperator(0)) # dummy measurement to make this a valid QNode
    
    return circuit

def squeezing_db(r_natural):
    """
    Convert squeezing parameters from natural units to decibels for reporting and threshold check.
    """

    return 10 * np.log10(np.exp(2 * np.abs(r_natural)))

if __name__ == "__main__":
    print("Computing GBS parameters from molecular vibronic data...")

    r_single, t_two, U1, U2, alpha = compute_gbs_params(w, w_prime, D, delta, T=0)

    max_squeezing_db = np.max(squeezing_db(r_single))
    print(f"\n Molecule : Formic Acid (HCOOH)")
    print(f" Vibrational modes : {N_MODES}")
    print(f" GBS circuit modes : {2*N_MODES} (including ancillas for thermal state)")
    print(f" Max Squeezing : {max_squeezing_db:.2f} dB")
    print(f" Mean Squeezing : {np.mean(squeezing_db(r_single)):.2f} dB")

    circuit = build_vibronic_circuit(r_single, t_two, U1, U2, alpha)

    dev = qml.device("default.gaussian", wires=2*N_MODES)
    runnable = qml.QNode(circuit, dev)
    mean_photon_number = runnable()
    print(f" Mean photon number on wire 0 (test run) : {mean_photon_number:.4f}")

    analyzer = CircuitAnalyzer(circuit, n_wires=2*N_MODES)
    gate_counts = analyzer.analyze()
    print("\nGate counts from circuit analysis:")
    gate_counts["max_squeezing_db"] = max_squeezing_db

    all_resources = {}
    for backend_name, overhead_model in BACKENDS.items():
        estimator = ResourceEstimator(overhead_model=overhead_model, squeezing_db=max_squeezing_db)
        resources = estimator.estimate(gate_counts)
        all_resources[backend_name] = resources
        print_report(backend_name, gate_counts, resources)

    # Noise sweep for GBS backend
    print("Sweeping loss rate for GBS backend...")
    sweep_results = sweep_loss_rate(gate_counts, backend="gbs")
    print_sweep(sweep_results)

    # Export results to CSV
    export_to_csv(gate_counts, all_resources, sweep_results=sweep_results)

    print("Hardware feasibility")
    for backend_name, resources in all_resources.items():
        if resources.get("hardware_warnings"):
            print(f"Backend '{backend_name}' has hardware warnings:")
            for w in resources["hardware_warnings"]:
                print(f"  - {w}")
        else:
            print(f"Backend '{backend_name}' has no hardware warnings. This circuit is likely feasible on current devices under the assumptions of this overhead model.")