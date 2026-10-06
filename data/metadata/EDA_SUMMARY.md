# Subsystem Exploratory Data Analysis (EDA) Summary Report

**Project Title:** Development of a Multi-Objective Reinforcement Learning Framework for Autonomous Satellite Power and Propulsion Management  
**Author:** Research Data Engineer + Aerospace Data Researcher  
**Date:** October 3, 2026  
**Status:** **READY — EDA STARTED WITH MASS PARAMETER EXCLUDED**

---

## Executive Summary

Independent Exploratory Data Analysis (EDA) was performed separately across the three cleaned subsystem datasets:
1. **Power Subsystem:** BIRDS-3 1U CubeSat Flight Telemetry (`power_subsystem.csv`, 1,080 rows)
2. **Orbit Subsystem:** CelesTrak Active Satellite GP Orbit Catalog (`orbit_subsystem.csv`, 14,931 rows)
3. **Propulsion Subsystem:** Spacecraft Thruster Firing Tests (`propulsion_subsystem.csv`, 2,342 clean nominal sequences)

The three datasets were maintained in **strict independence** (0 cross-spacecraft joins, 0 timestamp joins, 0 artificial telemetry synthesis). All EDA results presented below are purely **descriptive**, not confirmatory.

---

## 1. Mass Parameter Verification Outcome

* **Tested Parameter:** `birds3_1u_cubesat_mass_limit_kg = 1.33 kg`
* **Verification Result:** **`UNVERIFIED`**
* **Findings:** Inspection of the raw source files (`NEPALISAT.xlsx`, `celestrak_satellite_dataset_3-April-2026.csv`, `STFT Dataset Description.pdf`) confirmed that $1.33\text{ kg}$ is NOT explicitly provided as a documented parameter in the provided source files.
* **Action Taken:** Removed $1.33\text{ kg}$ from `subsystem_parameters.csv` Section A. Re-classified as `UNVERIFIED` in `FINAL_DATA_PROVENANCE.csv`. **EXCLUDED** from source-data EDA and simulation calibration. No substitute mass value was introduced.

---

## 2. Power Subsystem EDA

### 2.1 Dataset & Record Count
* **Source:** BIRDS-3 Satellite Project In-Orbit Telemetry (NepaliSat-1, Raavana-1, Tsuru, Uguisu).
* **Location:** [`data/processed/power_subsystem.csv`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/processed/power_subsystem.csv)
* **Record Count:** 1,080 rows × 18 columns.
* **Time Coverage:** Multi-day in-orbit pass telemetry recorded at 5-second sampling intervals.
* **Missing Values:** 0 missing records (0.0%).
* **Duplicates:** 0 duplicate rows.

### 2.2 Descriptive Statistics Table

| Variable | Classification | Unit | Mean | Std | Min | 50% (Median) | Max | Missing (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `battery_voltage_V` | `OBSERVED` | V | 4.0989 | 0.1230 | 3.8700 | 4.2000 | 4.2000 | 0.0% |
| `battery_current_A` | `OBSERVED` | A | 0.0053 | 0.2237 | -0.6532 | -0.0383 | 0.3307 | 0.0% |
| `battery_temp_C` | `OBSERVED` | °C | 6.6501 | 1.4421 | 4.5200 | 6.8200 | 8.7300 | 0.0% |
| `P_solar_total_W` | `DERIVED` | W | 1.1316 | 1.0193 | 0.0182 | 1.2768 | 4.1840 | 0.0% |
| `P_battery_W` | `DERIVED` | W | 0.0045 | 0.9091 | -2.7436 | -0.1608 | 1.2963 | 0.0% |
| `P_load_W` | `DERIVED` | W | 1.1361 | 0.1468 | 0.8256 | 1.1090 | 1.7039 | 0.0% |

### 2.3 Key Data Characteristics & Outliers
1. **BMS Voltage Clamping:** `battery_voltage_V` exhibits a sharp upper saturation limit at $4.20\text{ V}$ (50% and 75% quantiles equal $4.20\text{ V}$), reflecting standard battery management system (BMS) overcharge protection for 1S Li-ion cell chemistries.
2. **Eclipse Power Drop:** `P_solar_total_W` drops to near-zero ($0.0182\text{ W}$) during eclipse phases, while peaking at $4.1840\text{ W}$ under optimal solar vector alignment.
3. **Unclipped Load Power Derivation:** Derived bus load power ($P_{\text{load}} = P_{\text{solar}} + P_{\text{battery}}$) ranges continuously from $0.8256\text{ W}$ (idle/beacon mode) to $1.7039\text{ W}$ (active payload operation) with zero artificial clipping applied.

### 2.4 Unsuitable Variables & Exclusions
* **`SOC_PROXY` / 2.6 Ah:** Removed from EDA. Coulomb counting based on assumed cell capacity is not an observed telemetry variable.
* **Raw Integer ADC Columns:** Excluded from processed dataset as uncalibrated hardware units.

### 2.5 Implications for RL Simulation Model
* Solar array generation models must simulate solar vector angles and eclipse transitions ($P_{\text{solar}} \to 0\text{ W}$).
* Satellite bus load power ranges between $0.83\text{ W}$ and $1.70\text{ W}$, defining empirical power budget constraints for RL actions.

---

## 3. Orbit Subsystem EDA

### 3.1 Dataset & Record Count
* **Source:** CelesTrak Active Satellite General Perturbations (GP) Catalog.
* **Location:** [`data/processed/orbit_subsystem.csv`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/processed/orbit_subsystem.csv)
* **Record Count:** 14,931 catalog elements × 13 columns.
* **Epoch:** April 2026 snapshot.
* **Missing Values:** 0 missing records (0.0%).
* **Duplicates:** 0 duplicate rows.

### 3.2 Descriptive Statistics Table

| Variable | Classification | Unit | Mean | Std | Min | 50% (Median) | Max | Missing (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `inclination_deg` | `OBSERVED` | deg | 60.1125 | 30.8241 | 0.0000 | 53.0541 | 149.6827 | 0.0% |
| `eccentricity` | `OBSERVED` | dim. | 0.0024 | 0.0198 | 0.0000 | 0.0002 | 0.8962 | 0.0% |
| `mean_motion_rev_per_day`| `OBSERVED` | rev/day| 13.9182 | 2.5901 | 0.1558 | 15.0601 | 16.7118 | 0.0% |
| `altitude_km` | `OBSERVED` | km | 2256.09 | 5892.40 | 145.20 | 536.85 | 91537.47 | 0.0% |
| `semi_major_axis_a_km` | `DERIVED` | km | 8627.09 | 5892.40 | 6523.34 | 6909.99 | 97908.47 | 0.0% |
| `derived_perigee_altitude_km`| `DERIVED` | km | 2164.35 | 5824.12 | 138.42 | 533.80 | 36876.77 | 0.0% |
| `derived_apogee_altitude_km` | `DERIVED` | km | 2333.56 | 6013.18 | 151.18 | 540.21 | 173651.39| 0.0% |

### 3.3 Orbital Regime Breakdown

| Orbital Regime | Count | Percentage (%) | Mean Altitude (km) |
| :--- | :--- | :--- | :--- |
| **LEO** (Low Earth Orbit) | 14,120 | 94.57% | 584.2 km |
| **GEO** (Geostationary Orbit) | 592 | 3.97% | 35,786.1 km |
| **MEO** (Medium Earth Orbit) | 219 | 1.47% | 20,182.4 km |

### 3.4 Key Data Characteristics & Outliers
1. **LEO Dominance:** 94.57% of active satellites reside in LEO ($< 2,000\text{ km}$ altitude) with median altitude $536.85\text{ km}$.
2. **Eccentricity Distribution:** Median eccentricity is extremely low ($0.0002$), indicating near-circular operational orbits for most active payloads. Outliers ($e > 0.5$, max $0.8962$) represent highly elliptical transfer orbit objects.

### 3.5 Unsuitable Variables & Exclusions
* **Target Altitude (400 km) & Target Inclination (51.6°):** Excluded from source-data EDA. They are simulation choices, NOT CelesTrak catalog observations.
* **`orbit_error`:** Excluded from source-data EDA. Orbit deviation is a model-generated quantity in the future RL environment.

### 3.6 Implications for RL Simulation Model
* LEO satellite distribution validates selecting LEO altitude bounds ($300\text{--}800\text{ km}$) for the RL simulation state space.

---

## 4. Propulsion Subsystem EDA

### 4.1 Dataset & Record Count
* **Source:** Spacecraft Thruster Firing Tests (STFT) Dataset.
* **Classification:** **Physics-based synthetic hot-fire ground test data** (Patrick Fleith, 2021).
* **Location:** [`data/processed/propulsion_subsystem.csv`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/processed/propulsion_subsystem.csv)
* **Nominal Record Count:** 2,342 test sequences × 14 columns.
* **Excluded Anomalous Sequences:** 270 sequences (`anomalous == True` or `anomaly_code != 0`).
* **Missing Values:** 0 missing records (0.0%).
* **Duplicates:** 0 duplicate rows.

### 4.2 Descriptive Statistics Table

| Variable | Classification | Unit | Mean | Std | Min | 50% (Median) | Max | Missing (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `test_pressure` | `OBSERVED` | bars | 14.6072 | 6.2005 | 5.0000 | 15.0000 | 24.0000 | 0.0% |
| `cumulated_throughput` | `OBSERVED` | kg | 11.7329 | 6.2789 | 0.0000 | 12.8363 | 22.4897 | 0.0% |
| `cumulated_on_time` | `OBSERVED` | s (x10^5) | 3.4645 | 2.0732 | 0.0000 | 3.2707 | 7.3683 | 0.0% |
| `cumulated_pulses` | `OBSERVED` | count | 10595.08| 6784.19 | 0.0000 | 9669.0000 | 23653.0000| 0.0% |
| `anomalous` | `OBSERVED` | bool | False | N/A | False | False | False | 0.0% |
| `anomaly_code` | `OBSERVED` | int | 0 | N/A | 0 | 0 | 0 | 0.0% |

### 4.3 Key Data Characteristics
1. **Pressure Discretization:** `test_pressure` is sampled at discrete ground test bench levels ($5, 9, 12, 15, 18, 21, 24\text{ bars}$) with mean $14.61\text{ bars}$.
2. **Cumulative Ageing Factors:** `cumulated_throughput` (propellant mass throughput up to $22.49\text{ kg}$) and `cumulated_pulses` (up to $23,653$ pulses) provide degradation tracking metrics.

### 4.4 Unsuitable Variables & Exclusions
* **Synthetic Thruster Formulas (`0.4*p`, `160*p`):** Completely purged.
* **Fixed $I_{sp}$ (225 s):** Excluded from source-data EDA. Not documented as a fixed constant in STFT source PDF.
* **Spacecraft Wet Mass:** STFT ground test documentation does NOT specify a satellite mass. Excluded from EDA.

### 4.5 Implications for RL Simulation Model
* Firing dynamics depend on inlet pressure ($5\text{--}24\text{ bars}$) and cumulative propellant throughput, providing empirical grounding for thruster impulse curves in the RL simulation environment.

---

## 5. Summary of EDA Output Files Created

```text
data/eda/
├── power/
│   ├── power_descriptive_stats.csv
│   └── power_correlation_matrix.csv
├── orbit/
│   ├── orbit_descriptive_stats.csv
│   ├── orbit_correlation_matrix.csv
│   └── orbit_regime_distribution.csv
└── propulsion/
    ├── propulsion_descriptive_stats.csv
    ├── propulsion_correlation_matrix.csv
    └── propulsion_test_mode_counts.csv
```

---

## FINAL STATUS

```text
READY — EDA STARTED WITH MASS PARAMETER EXCLUDED
```
