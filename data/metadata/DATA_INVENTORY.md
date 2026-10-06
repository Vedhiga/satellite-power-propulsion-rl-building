# Projects/Data Raw & Processed Dataset Inventory

**Project Title:** Development of a Multi-Objective Reinforcement Learning Framework for Autonomous Satellite Power and Propulsion Management  
**Author:** Research Data Engineer + Aerospace Data Researcher  
**Date:** October 2, 2026  

---

## 1. Power / EPS Subsystem Dataset

* **Dataset:** BIRDS On-orbit Electrical Power System (EPS) Dataset
* **Source:** Mendeley Data ([DOI: 10.17632/8kp25ycf63.1](https://doi.org/10.17632/8kp25ycf63.1)) / GitHub ([BIRDSOpenSource/EPS_dataset](https://github.com/BIRDSOpenSource/EPS_dataset)) / *Data in Brief* ([DOI: 10.1016/j.dib.2022.108697](https://doi.org/10.1016/j.dib.2022.108697))
* **Local Path:** `projects/data/8kp25ycf63-1.zip` (Extracted raw: `projects/data/raw/power/8kp25ycf63-1/`)
* **Files:** `NEPALISAT.xlsx`, `RAAVANA.xlsx`, `TSURU.xlsx`, `UGUISU.xlsx`
* **File Format:** Microsoft Excel (`.xlsx`)
* **Rows:** 
  * `NEPALISAT.xlsx`: 1,080 records
  * `RAAVANA.xlsx`: 1,079 records
  * `TSURU.xlsx`: 8,820 records
  * `UGUISU.xlsx`: 1,072 records
* **Columns:** 37 columns per file (`Time Stamp`, battery voltage/current/temp, 5-face solar panel voltages/currents/temps)
* **Time Range:** 2017-07 to 2021-04 (Full operational lifespan)
* **Sampling/Resolution:** 90 seconds (nominal operation) to 10 seconds (fast mode during pass)
* **License/Usage Information:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## 2. Orbit / Trajectory Subsystem Dataset

* **Dataset:** CelesTrak Active Satellite Dataset (April 2026 Snapshot)
* **Source:** Kaggle (`bhaktimudgal/celestrak-active-satellite-dataset-april-2026`) / CelesTrak GP Orbit Catalog
* **Local Path:** `projects/data/archive (7).zip` (Extracted raw: `projects/data/raw/orbit/celestrak_satellite_dataset_3-April-2026.csv`)
* **Files:** `celestrak_satellite_dataset_3-April-2026.csv`
* **File Format:** Comma-Separated Values (`.csv`)
* **Rows:** 14,931 active satellite orbit records
* **Columns:** 10 columns (`name`, `epoch`, `inclination_deg`, `raan_deg`, `eccentricity`, `arg_perigee_deg`, `mean_anomaly_deg`, `mean_motion_rev_per_day`, `altitude_km`, `orbit_type`)
* **Time Range:** Epoch 2026-04-02 / April 2026 active catalog snapshot
* **Sampling/Resolution:** Static orbital element snapshot across LEO, MEO, GEO, and HEO satellites
* **License/Usage Information:** Open Access / CelesTrak Public Domain Data

---

## 3. Propulsion Subsystem Dataset

* **Dataset:** Spacecraft Thruster Firing Tests Dataset (STFT)
* **Source:** Kaggle (`patrickfleith/spacecraft-thruster-firing-tests-dataset`)
* **Local Path:** `projects/data/archive (6).zip` (Extracted raw PDF: `projects/data/raw/propulsion/STFT Dataset Description.pdf`)
* **Files:** `archive (6).zip` (contains 2,612 CSV files) and `STFT Dataset Description.pdf`
* **File Format:** CSV files (`.csv`) + Documentation PDF (`.pdf`)
* **Rows:** 2,612 individual hot fire test time-series CSV files (each containing 1,000 to 30,000 timesteps recorded at 100 Hz)
* **Columns:** 6 columns per CSV (`Timestamps`, `ton`, `thrust`, `mfr`, `vl`, `anomaly_code`)
* **Time Range:** Synthetic hot fire test durations (10 seconds to 300 seconds per test)
* **Sampling/Resolution:** 100 Hz high-frequency telemetry logging
* **License/Usage Information:** Open Access / Creative Commons License (Synthetic physics-based monopropellant thruster test dataset)
* **Usage Rule:** Sequences with `anomaly_code != 0` or `anomalous == True` are explicitly **EXCLUDED** from nominal model calibration.
