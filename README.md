# Photonic Resource Estimator

A hardware-aware analysis tool that maps PennyLane photonic circuits to physical resource counts on Xanadu's Gaussian Boson Sampling (GBS) and cluster-state backends

## Motivation
- PennyLane's built-in estimator counts logical gates (CNOT, Hadamard, T-gates) for qubit machines. This tool prototype counts physical photonic components : Squeezed light sources, beamsplitters, detectors, etc. on continous variable hardware. This tool is built to address the hardware cost bottleneck for photonic computation estimation.

### Installation

#### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed on your system
- Python 3.14 or higher

#### Quick Start with uv

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sri-Harsha-T/photon-resource-estimator
   cd photonic-resource-estimator
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   uv sync
   ```
   This creates a virtual environment and installs all dependencies specified in `pyproject.toml`.

3. **Verify installation**
   ```bash
   uv run python -c "import pennylane; import strawberryfields; print('Installation successful!')"
   ```

#### Common uv Commands

- **Run the main script**
  ```bash
  uv run python main.py
  ```

- **Run demos**
  ```bash
  uv run python demos/vibronic_formic_acid.py
  ```

- **Add a new dependency**
  ```bash
  uv pip install <package-name>
  ```

- **Activate the virtual environment** (for interactive use)
  ```bash
  # On Windows
  .venv\Scripts\activate
  
  # On macOS/Linux
  source .venv/bin/activate
  ```

- **Run Python with the project environment**
  ```bash
  uv run python <script.py>
  ```

#### Installation Details

The `uv sync` command will:
- Detect your Python version (requires >=3.14)
- Create a `.venv` virtual environment
- Install all dependencies: `numpy`, `pennylane`, `rich`, `setuptools`, `strawberryfields`
- Lock versions in `uv.lock` for reproducible builds

### Usage

```bash
# Quick estimation on custom circuit
python main.py

# Run the real demo on PennyLane implementation of estimation of photonic hardware for GBS Vibronic spectra of formic acid
python demos/vibronic_formic_acid.py

# Export results to CSV
python demos/vibronic_formic_acid.py --export
```

## Features

**Gate-level tape analysis** : Parses a PennyLane circuit tape without executing it and extracts the squeezing, beamsplitter, rotation and displacement operation counts alongside circuit depth.

**Backend comparison** : Estimates resources under multiple photonic architecture models. (GBS and cluster state measurement based backend computations here, can be modified).

**Noise model sweep** : Provides a trend of Optical loss rate (sweep) across a configurable range (default here : 1% to 15%) and records how the detector, squeezed source counts and overhead factors scale. Can produce a table and optional CSV for plotting.

**Squeezing threshold warning** : Compares requested squeezing level against the current set hardware ceiling of 15 dB per mode. The model flags circuits that are not physically realizable based on current devices' constraints. (both per-operation and as a total budget across modes).

## How this differs from `qml.estimator`

This tool is supposed to complement the `qml.estimator` tool. `qml.estimator` answers "how many logical operations does this algorithm need on a perfect machine?" This tool answers the limitations to make the circuit a reality, about "how many physical photonic components does it need on Photonic (Xanadu's) hardware?"

| | `qml.estimator` | This tool |
|---|---|---|
| Computational model | Qubit gate model | Continous variable photonic |
| What this counts? | Hadamard, CNOT, T-gates | Squeezed sources, beamsplitters, detectors |
| Noise modeling | - | 15dB squeezing ceiling |
| Backend comparison | Not applicable | GBS vs Cluster state (can be modified) |
| Target user | Algorithm designer | Hardware architect |

## Backend overhead models

| Parameter\Backend | GBS | Cluster state |
|---|---|---|
| Squeezer overhead | 1x | 1.5x |
| Beamsplitter overhead | 1x | 2x (network of beamsplitters for entanglement) |
| Detector overhead | 1x per mode | 1x per mode | 
| Ancilla mode ratio | 20% | 50% |
| Loss overhead factor | 1.25x (baseline) | 1.5x (baseline) |
| Default squeezing lvl| 15dB | 12dB |

## Known limitations

**Uniform loss model** : Loss overhead is applied uniformly per circuit layer. Real photonic devices might have mode-dependent loss profiles with waveguide propagation and coupling loss at each component. Add varying detector inefficiency to contribute further loss. Per-component loss rates' assignment can make this a more accurate model.

**No compliation step** : The tool estimator reads the circuit as is written. This doesn't take into the consideration that a compiler might reorder or fuse gates to reduce depth and mode count. Hence, this tool can provide a conservative estimation for circuits that might not have been optimized yet.

**Approximate cluster state overhead** : The counts for cluster state backend assume generic measurement based protocol. Actual overhead might change on the encoding, state graph and measurement sequences. Based on the correction strategies and encodings, the same algorithm can have different resource costs.

## References 
(Including Demo)

[1] Huh, J., Guerreschi, G.G., Peropadre, B., McClean, J.R., and Aspuru-Guzik, A. "Boson sampling for molecular vibronic spectra." *Nature Photonics* 9, 615–620 (2015). doi:[10.1038/nphoton.2015.153](https://doi.org/10.1038/nphoton.2015.153)
 
[2] Bromley, T.R. et al. "Applications of near-term photonic quantum computers: software and algorithms." *Quantum Science and Technology* 5, 034010 (2020). arXiv:[1912.07634](https://arxiv.org/abs/1912.07634)
 
[3] Hamilton, C.S. et al. "Gaussian boson sampling." *Physical Review Letters* 119, 170501 (2017). arXiv:[1612.01199](https://arxiv.org/abs/1612.01199)
 
[4] Killoran, N. et al. "Strawberry Fields: a software platform for photonic quantum computing." *Quantum* 3, 129 (2019). doi:[10.22331/q-2019-03-11-129](https://doi.org/10.22331/q-2019-03-11-129)

## License

Apache License 2.0 - consistent with PennyLane and Strawberry Fields