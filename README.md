# Multi-Objective Reinforcement Learning Framework for Autonomous Satellite Power and Propulsion Management

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A physics-based, data-grounded simulation environment and multi-objective reinforcement learning benchmark for small satellite low Earth orbit (LEO) station-keeping and power management.

---

## 📌 Project Overview

Autonomous satellite operations require balancing competing physical constraints across subsystems:
1. **Orbital Station-Keeping:** Counteracting exponential atmospheric drag in LEO ($400\text{ km}$) to prevent orbital decay.
2. **Electrical Power Management:** Balancing solar array generation ($P_{\text{solar}} = 8.0\text{ W}$) against bus loads and eclipse shadows ($35\%\text{ of orbit}$).
3. **Propellant Conservation:** Minimizing cold-gas / monopropellant mass expulsion ($m_{\text{dot}} = 0.45\text{ g/s}$).
4. **Subsystem Safety & Health:** Avoiding deep battery discharge ($SOC < 20\%$) and payload thermal brownouts.

This repository provides a modular, lightweight, high-speed Python simulation environment (`UnifiedSatelliteEnv`) calibrated against authentic flight telemetry (BIRDS-3 1U CubeSats) and physics-based ground-test thruster datasets (STFT).

---

## 📐 Mathematical Formulation

### 1. Orbital Dynamics & Drag Decay
Atmospheric density $\rho$ is modeled using an exponential scale-height formulation:
$$\rho(h) = \rho_0 \exp\left(-\frac{h - h_0}{H}\right)$$
where $\rho_0 = 2.7 \times 10^{-12}\text{ kg/m}^3$, $h_0 = 400.0\text{ km}$, and $H = 50.0\text{ km}$.

The atmospheric drag decay rate $\frac{da}{dt}$ (King-Hele model) is:
$$\frac{da}{dt} = -\rho \sqrt{\mu r} \frac{C_d A}{m_{\text{total}}}$$

The velocity increment $\Delta v$ from a thruster burn of duration $\Delta t_{\text{burn}}$ is:
$$\Delta v = \frac{F_{\text{thrust}} \Delta t_{\text{burn}}}{m_{\text{total}}}, \quad F_{\text{thrust}} = \dot{m} g_0 I_{\text{sp}}$$

The impulsive altitude boost $\Delta h_{\text{boost}}$ via the Vis-Viva relation is:
$$\Delta h_{\text{boost}} = \frac{2 r}{v_{\text{orb}}} \Delta v, \quad v_{\text{orb}} = \sqrt{\frac{\mu}{r}}$$

### 2. Electrical Power System (EPS) & Energy Balance
Solar generation $P_{\text{gen}}$ follows orbital lighting geometry:
$$P_{\text{gen}} = \begin{cases} 0.0\text{ W}, & \text{if } \text{phase} < \phi_{\text{eclipse}} \\ P_{\text{solar,max}} (8.0\text{ W}), & \text{if } \text{phase} \ge \phi_{\text{eclipse}} \end{cases}$$

Total bus power consumption $P_{\text{bus}}$ couples payload power mode and thruster valve draw:
$$P_{\text{bus}} = P_{\text{mode}} + P_{\text{valves}} \frac{\Delta t_{\text{burn}}}{\Delta t}$$
$$\Delta SOC = \frac{(P_{\text{gen}} - P_{\text{bus}}) \Delta t}{V_{\text{bat}} C_{\text{bat,coulombs}}}$$

### 3. State & Action Discretization
* **State Space ($S \in [0, 119]$):** $5 \times 4 \times 3 \times 2 = 120$ discrete states encoding:
  - Altitude Bin (5): $[<-10, -10..-2, -2..+2, +2..+10, >+10\text{ km}]$
  - Battery SOC Bin (4): $[<20\%, 20..40\%, 40..80\%, \ge 80\%]$
  - Propellant Bin (3): $[<25\%, 25..60\%, \ge 60\%]$
  - Illumination State Bin (2): $[0: \text{Eclipse}, 1: \text{Sunlight}]$
* **Action Space ($A \in [0, 8]$):** 9 discrete action tuples $(P_{\text{mode}}, \Delta t_{\text{burn}})$:
  - Modes: `0: Safe (2W)`, `1: Standard (5W)`, `2: Payload (12W)`
  - Burns: `0.0 s`, `2.0 s`, `10.0 s`

### 4. Multi-Objective Cost & Reward Function
$$C = 0.4 \cdot \hat{e}_{\text{orbit}} + 0.3 \cdot \hat{m}_{\text{fuel}} + 0.1 \cdot \hat{P}_{\text{bus}} + 0.2 \cdot B_{\text{penalty}}$$
$$R = -C$$
where $B_{\text{penalty}} = 10.0$ if $SOC < 0.20$, else $\left(\frac{0.40 - SOC}{0.20}\right)^2$ if $SOC < 0.40$, else $0.0$.

---

## 📂 Repository Structure

```text
.
├── .gitignore                  # Git ignore file for python caches and virtualenvs
├── requirements.txt            # Minimal pinned dependencies
├── README.md                   # Project documentation
├── src/                        # Main source package
│   ├── __init__.py
│   ├── config.py               # SatelliteConfig dataclass & physical parameters
│   ├── subsystems/             # Physics subsystem implementations
│   │   ├── __init__.py
│   │   ├── propulsion.py       # PropulsionSubsystem (burns, delta-v, valve power)
│   │   ├── orbit.py            # OrbitDynamics (King-Hele drag decay & Vis-Viva boost)
│   │   └── power.py            # PowerSubsystem (eclipse geometry, solar gen, SOC)
│   ├── envs/                   # Simulation environments
│   │   ├── __init__.py
│   │   └── satellite_env.py    # UnifiedSatelliteEnv (Gym-style MDP)
│   └── controllers/            # Baseline controllers
│       ├── __init__.py
│       └── rule_based.py       # Deterministic RuleBasedController
├── tests/                      # Automated test suite
│   ├── __init__.py
│   └── test_environment_validation.py # Deterministic verification tests (1, 2, 3 & Edge Cases)
├── experiments/                # Experiment driver scripts
│   └── run_baseline.py         # 100-step baseline evaluation script
└── data/                       # Data assets and results
    ├── metadata/               # Data provenance & EDA metadata
    └── results/                # Output evaluation logs & baseline_metrics.json
```

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/satellite-rl-power-propulsion.git
cd satellite-rl-power-propulsion

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Running the Verification Test Suite

Run the deterministic test suite using `pytest`:
```bash
pytest tests/test_environment_validation.py -v
```
All 8 test cases verify:
* **Test 1:** Propulsion-to-orbit coupling (drag decay vs 10s burn boost $> 1.0\text{ km}$).
* **Test 2:** Solar power generation & energy balance (eclipse discharge vs sunlight charging).
* **Test 3:** Thruster valve power draw coupling & nonlinear battery safety penalty ($10.0$).
* **Edge Cases A–E:** Propellant depletion, battery overcharge saturation, terminal brownout ($SOC < 15\%$), terminal re-entry ($h < 350\text{ km}$), and state index bounds ($0 \le s \le 119$).

---

## 📊 Running the Baseline Simulation Evaluation

Execute the 100-step baseline evaluation script (~1.6 LEO orbits):
```bash
python experiments/run_baseline.py
```

### Summary Baseline Performance Benchmark
```text
================================================================================
                      BASELINE EVALUATION SUMMARY METRICS                       
================================================================================
  Cumulative Reward            : -45.1974
  Mean Tracking Error (km)     : 1.6366 km
  Total Propellant Expended (g): 18.0000 g
  Final Battery SOC (%)        : 73.06 %
  Final Altitude (km)          : 399.7363 km
================================================================================
```
Output trajectory logs and metrics are exported to [`data/results/baseline_metrics.json`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/results/baseline_metrics.json).

---

## 🛠️ GitHub Deployment Instructions

To initialize this project as a Git repository and push it to GitHub, run the following CLI commands:

```bash
# 1. Initialize local repository
git init

# 2. Add all files to staging
git add .

# 3. Create initial commit
git commit -m "feat: initial release of modular satellite RL power & propulsion simulation framework"

# 4. Rename default branch to main
git branch -M main

# 5. Link to your GitHub remote repository (replace URL with your repository)
git remote add origin https://github.com/your-username/satellite-rl-power-propulsion.git

# 6. Push local commits to remote main branch
git push -u origin main
```

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
