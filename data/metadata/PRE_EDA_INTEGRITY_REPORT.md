# Pre-EDA Data Integrity Audit & Pipeline Correction Report

**Project Title:** Development of a Multi-Objective Reinforcement Learning Framework for Autonomous Satellite Power and Propulsion Management  
**Author:** Lead Research Data Engineer + Aerospace Data Researcher  
**Date:** October 3, 2026  
**Final Pre-EDA Determination:** **READY FOR EDA**

---

## 1. Summary of Changes Made

We have executed a comprehensive data-integrity cleanup of the preprocessing pipeline under `projects/data/` prior to initiating Exploratory Data Analysis (EDA):

1. **Complete Removal of Synthetic Generators:** All random generators (`np.random`), hardcoded thruster scaling equations (`0.4 * p`), and synthetic thruster IDs (`SN_NOMINAL_RCT`) have been removed from active processing.
2. **Battery SoC Proxy Removed from EDA:** The Coulomb-counting calculation using assumed \(Q_{\text{nom}} = 2.6\text{ Ah}\) has been removed from `power_subsystem.csv`. \(2.6\text{ Ah}\) is isolated as an `ASSUMPTION` / `MODEL_PARAMETER` in `subsystem_parameters.csv`.
3. **Orbit Target & Orbit Error Removed from EDA:** Target altitude (\(400\text{ km}\)), target inclination (\(51.6^\circ\)), and calculated `orbit_error` have been removed from `orbit_subsystem.csv`.
4. **Propulsion Nominal Sequence Filtering:** `propulsion_subsystem.csv` is now constructed directly from actual STFT `metadata.csv` (2,612 test sequences). All 270 anomalous sequences (`anomalous == True` or `anomaly_code != 0`) have been explicitly **EXCLUDED** from nominal model calibration.
5. **Strict Power Unit Detection:** Fixed unit detection logic in `power_column_audit.csv` using strict regex/substring matching (`(mV)`, `(V)`, `(mA)`, `(C)`, `°C`, `(raw)`), eliminating false matches.
6. **Separation of Raw Data:** All raw files in `projects/data/raw/` (`8kp25ycf63-1.zip`, `archive (6).zip`, `archive (7).zip`) remain 100% unmodified.

---

## 2. Generated-Data Logic Removed (Rule 1 Audit)

The following synthetic generation logic from previous iterations has been completely purged from active data scripts:
* `nominal_thrust_N = round(0.4 * p, 2)` (Removed)
* `nominal_mfr_mg_s = round(160.0 * p, 2)` (Removed)
* Synthetic thruster profiles: `SN_NOMINAL_RCT`, `CLEAN_NOMINAL`, `[5, 9, 12, 15, 18, 21, 24]` pressure points (Removed)
* Fallback `np.random` generators in network fetch scripts (Removed)

---

## 3. Unsupported Parameters Removed from EDA

* `SOC_PROXY` (Removed from observed power dataset for EDA; preserved as model parameter assumption).
* `target_orbit_altitude_km`, `target_orbit_inclination_deg` (Removed from orbit dataset for EDA).
* `orbit_error` (Removed from EDA dataset).
* `propellant_mass_remaining_kg` (Removed from BIRDS EPS dataset).

---

## 4. Battery SoC Status (Rule 3 Audit)

* **EDA Status:** `SOC_PROXY` is **NOT** present in `processed/power_subsystem.csv`.
* **Reason:** \(2.6\text{ Ah}\) is an external battery cell specification rating, NOT a direct telemetry measurement in `NEPALISAT.xlsx`.
* **EDA Analysis:** EDA will analyze directly observed voltage (`battery_voltage_V`), current (`battery_current_A`), temperature (`battery_temp_C`), panel voltages/currents, and derived power ($P = V \times I$).

---

## 5. Orbit-Error Status (Rule 4 & 5 Audit)

* **EDA Status:** `orbit_error = NOT AVAILABLE IN EDA`.
* **Reason:** CelesTrak active satellite dataset is an orbital element catalog (14,931 satellites). Target orbit choices ($400\text{ km}$, $51.6^\circ$) belong to the simulation environment design phase, NOT EDA.
* **EDA Analysis:** EDA will analyze actual observed orbital elements: `inclination_deg`, `raan_deg`, `eccentricity`, `arg_perigee_deg`, `mean_anomaly_deg`, `mean_motion_rev_per_day`, and derived semi-major axis / perigee / apogee altitudes.

---

## 6. Propulsion Processing Status (Rule 2 & 9 Audit)

* **Source:** STFT (Spacecraft Thruster Firing Tests) dataset (`archive (6).zip` / `stft_metadata.csv`).
* **Filtering Applied:**
  * Total Test Sequences: 2,612
  * Excluded Anomalous Sequences: 270 sequences (where `anomalous == True` or `anomaly_code \in [1..6]`)
  * Clean Nominal Sequences Retained: 2,342 sequences
* **Recorded Parameters:** `test_pressure` (bars), `cumulated_throughput` (kg), `cumulated_on_time` (s), `cumulated_pulses`, and 100 Hz time-series variables (`ton`, `thrust`, `mfr`, `vl`, `anomaly_code`).

---

## 7. Unit-Detection Correction (Rule 6 Audit)

Unit detection pattern matching in `power_column_audit.csv` was updated to avoid over-broad `'C' in col` matching:

```python
if '(mV)' in col:
    unit = 'mV'
elif '(V)' in col:
    unit = 'V'
elif '(mA)' in col:
    unit = 'mA'
elif '(C)' in col or '°C' in col:
    unit = '°C'
elif '(raw)' in col:
    unit = 'ADC Counts'
elif 'Time' in col:
    unit = 'UTC String'
else:
    unit = 'Unknown'
```

Regenerated metadata: [`projects/data/metadata/power_column_audit.csv`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/metadata/power_column_audit.csv).

---

## 8. Dataset Separation Confirmation (Rule 8 Audit)

The three datasets are maintained in strict independence:
1. **BIRDS EPS Dataset:** `projects/data/processed/power/power_subsystem.csv` (Power & battery characterization)
2. **CelesTrak Dataset:** `projects/data/processed/orbit/orbit_subsystem.csv` (Orbit characterization)
3. **STFT Propulsion Dataset:** `projects/data/processed/propulsion/propulsion_subsystem.csv` (Propulsion characterization)

They are **NOT** joined by timestamp, row index, or satellite ID.

---

## 9. List of Model Parameters Retained Separately

Saved in [`projects/data/processed/subsystem_parameters.csv`](file:///c:/Users/Vedhiga%20V.B/OneDrive/Desktop/RL/projects/data/processed/subsystem_parameters.csv):
* `solaero_z4j_Voc_V`: $3.72\text{ V}$ (SolAero Z4J+ Datasheet)
* `solaero_z4j_Vmp_V`: $3.31\text{ V}$ (SolAero Z4J+ Datasheet)
* `solaero_z4j_efficiency_bol_pct`: $31.3\%$ (SolAero Z4J+ Datasheet)
* `stft_nominal_thruster_isp_s`: $225.0\text{ s}$ (STFT Monopropellant RCT Physics)

---

## 10. List of Assumptions Retained Separately

* `birds3_nominal_battery_capacity_ah`: $2.6\text{ Ah}$ (Assumed 18650 Li-ion cell pack rating for simulation)
* `target_orbit_altitude_km`: $400.0\text{ km}$ (Assumed target LEO altitude for simulation)
* `target_orbit_inclination_deg`: $51.6^\circ$ (Assumed target LEO inclination for simulation)
* `spacecraft_wet_mass_kg`: $12.0\text{ kg}$ (Assumed nominal 6U/12U wet mass for rocket equation)

---

## 11. List of Files Marked DO NOT USE

The following files from previous iterations outside `projects/data/` contain synthetic/fallback records or invalid composite merging and are marked:
$$\textbf{DO NOT USE — PROVENANCE/INTEGRITY ISSUE}$$

1. `satellite_rl_real_data/processed/unified_satellite_dataset.csv` (Merged BIRDS EPS with ESA thrusters into a single fake spacecraft)
2. `satellite_rl_real_data/raw/birds3_eps_telemetry_raw.csv` (Contained synthetic fallback generator when network download failed)
3. `satellite_rl_real_data/raw/esa_adb_kepler_propulsion_raw.csv` (Contained synthetic thruster fallback generator)

---

## 12. Final Determination

### READY FOR EDA
