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
