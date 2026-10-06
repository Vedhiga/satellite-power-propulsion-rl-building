# Final Data Readiness & Integrity Report

**Project Title:** Development of a Multi-Objective Reinforcement Learning Framework for Autonomous Satellite Power and Propulsion Management  
**Author:** Lead Research Data Engineer + Aerospace Data Researcher  
**Date:** October 2, 2026  
**Final Status:** **READY FOR SIMULATION MODEL DESIGN**

---

## 1. Subsystem Data Readiness Summary Table

| Subsystem | Dataset | Available Variables | Derived Variables | Missing Variables | Required Assumptions | Ready? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Power/EPS** | BIRDS EPS (`NEPALISAT.xlsx`, etc.) | \(V_{\text{batt}}, I_{\text{batt}}, T_{\text{batt}}\), 5-face \(V_{p*}, I_{p*}\) | \(P_{\text{solar}}, P_{\text{battery}}, P_{\text{load}}, \text{SOC\_PROXY}\) | Detailed single-diode internal cell resistances | 100% Coulomb efficiency, 2.6 Ah nominal battery pack | **YES** |
| **Orbit** | CelesTrak Active Catalog (April 2026) | \(i, e, n, \Omega, \omega, M\), epoch, \(h\) | \(a, r_{\text{perigee}}, r_{\text{apogee}}\), SGP4 ECI state vectors, Eclipse status | Continuous 3-axis attitude pointing vector | SGP4 analytical propagation, circular LEO target orbit baseline | **YES** |
| **Propulsion** | Spacecraft Thruster Firing Tests (STFT) | `ton`, `thrust`, `mfr`, `vl`, `anomaly_code` | \(\Delta m = \int \text{mfr}\,dt\), \(I = \int F\,dt\), \(I_{sp} = I / (\Delta m g_0)\) | Spacecraft wet mass in raw STFT files | Nominal 12 kg wet mass, hydrazine monopropellant RCT physics | **YES** |

---

## 2. Explicit Audit Questions & Answers

1. **Can solar power be modeled?**  
   **YES.** Solar power is calculated across 5 faces as \(P_{\text{solar}} = \sum_{i=1}^5 V_i I_i \times 10^{-6}\) [Watts] (labeled `DERIVED`). SolAero Z4J+ datasheet parameters (\(V_{oc} = 3.72\text{ V}, \eta = 31.3\%\)) calibrate cell efficiency.
2. **Can battery behavior be modeled?**  
   **YES.** Measured battery terminal voltage (\(V_{\text{batt}}\)), charge/discharge current (\(I_{\text{batt}}\)), and pack temperature (\(T_{\text{batt}}\)) provide empirical V-I-T curves under dynamic load.
3. **Can SOC be obtained or only estimated?**  
   **ESTIMATED ONLY.** Labeled `SOC_PROXY` using Coulomb counting: \(\text{SOC\_PROXY}(t) = \text{SOC}_0 + \frac{100\%}{Q_{\text{nom}}} \int I_{\text{batt}} dt\).
4. **Can eclipse be determined?**  
   **YES.** Determined geometrically using SGP4 satellite position vectors and Earth-Sun conical shadow dot-product tests (0: Sunlight, 1: Penumbra, 2: Umbra).
5. **Can orbital state be represented?**  
   **YES.** SGP4 propagation converts CelesTrak GP orbital elements into ECI position vectors \(\mathbf{r}_{\text{ECI}}\) [km] and velocity vectors \(\mathbf{v}_{\text{ECI}}\) [km/s].
6. **Can orbit error be defined?**  
   **YES.** Defined as Option A Euclidean distance to reference trajectory: \(O_t = \|\mathbf{r}_t - \mathbf{r}_{\text{target},t}\|\).
7. **Can propulsion actions be represented?**  
   **YES.** Represented as commanded valve status \(\text{ton} \in \{0, 1\}\) and pulse duration \(\Delta t\).
8. **Can thrust be represented?**  
   **YES.** Thrust force \(F\) [N] is logged at 100 Hz frequency.
9. **Can propellant consumption be represented?**  
   **YES.** Mass flow rate `mfr` [mg/s] yields cumulative propellant consumption \(\Delta m = \int \text{mfr} \, dt\) [kg].
10. **What information is missing?**  
    Continuous 3-axis fine attitude pointing vector and internal single-diode solar cell resistances.
11. **What assumptions are required?**  
    Nominal 12 kg satellite wet mass, 2.6 Ah nominal 18650 battery pack capacity, circular target LEO orbit.
12. **Which quantities are observed?**  
    \(V_{\text{batt}}, I_{\text{batt}}, T_{\text{batt}}, V_{p*}, I_{p*}, i, e, n, \Omega, \omega, M, \text{ton}, F, \text{mfr}\).
13. **Which quantities are derived?**  
    \(P_{\text{solar}}, P_{\text{battery}}, P_{\text{load}}, \text{SOC\_PROXY}, a, h, \mathbf{r}_{\text{ECI}}, \mathbf{v}_{\text{ECI}}, O_t, \Delta m, I, I_{sp}\).
14. **Are any anomalous records present?**  
    **YES.** The STFT propulsion dataset contains anomalous sequences (`anomaly_code 1-6`). They have been **EXCLUDED** from nominal model calibration.
15. **Are any synthetic/random/fallback values present in the existing project?**  
    **FLAGGED:** `DO NOT USE — PROVENANCE/INTEGRITY ISSUE`. The previous script `download_data.py` created random fallback CSV files outside `projects/data/`. Those fallback CSVs have been discarded. The raw archives in `projects/data/` (`8kp25ycf63-1.zip`, `archive (6).zip`, `archive (7).zip`) are authentic.
16. **Are there any previously generated or incorrectly merged datasets that should NOT be used?**  
    **FLAGGED:** `DO NOT USE — PROVENANCE/INTEGRITY ISSUE`. The file `unified_satellite_dataset.csv` from Phase 1 merged BIRDS EPS and ESA thrusters into a single fictional spacecraft. It MUST NOT BE USED.

---

## 3. Dataset Discovery Summary

* **Power / EPS:** `projects/data/8kp25ycf63-1.zip` (Extracted: `projects/data/raw/power/8kp25ycf63-1/`). Source: Mendeley Data DOI `10.17632/8kp25ycf63.1`.
* **Orbit:** `projects/data/archive (7).zip` (Extracted: `projects/data/raw/orbit/celestrak_satellite_dataset_3-April-2026.csv`). Source: Kaggle `bhaktimudgal/celestrak-active-satellite-dataset-april-2026`.
* **Propulsion:** `projects/data/archive (6).zip` (Extracted PDF: `projects/data/raw/propulsion/STFT Dataset Description.pdf`). Source: Kaggle `patrickfleith/spacecraft-thruster-firing-tests-dataset`.

---

## 4. Dataset Verification Summary

All three downloaded dataset archives inside `projects/data/` were verified to match their intended scientific sources:
* **BIRDS EPS:** Contains authentic flight telemetry spreadsheets for 4 1U CubeSats (NepaliSat-1, Raavana-1, Tsuru, Uguisu).
* **CelesTrak:** Contains 14,931 active satellite GP orbit element sets snapshot for April 2026.
* **STFT Propulsion:** Contains 2,612 synthetic physics-based monopropellant thruster hot fire test CSVs recorded at 100 Hz.

---

## 5. Subsystem Characterization Architecture

The three datasets parameterize three independent simulation submodels inside our **Integrated Satellite Environment (Gymnasium)**:

```text
┌──────────────────────────────────────────────┐
│  1. BIRDS EPS Dataset                        │
└──────────────────────┬───────────────────────┘
                       │ Calibrates Solar Power & Battery BMS Submodel
                       ▼
┌──────────────────────────────────────────────┐
│  2. CelesTrak Active Satellite Dataset       │
└──────────────────────┬───────────────────────┘
                       │ Calibrates SGP4 Orbit & Target Path Submodel
                       ▼
┌──────────────────────────────────────────────┐
│  3. Spacecraft Thruster Firing Tests (STFT)  │
└──────────────────────┬───────────────────────┘
                       │ Calibrates Monopropellant Thruster Impulse & Mass Loss Submodel
                       ▼
┌────────────────────────────────────────────────────────┐
│  HYPOTHETICAL INTEGRATED SATELLITE SIMULATION (Gym)    │
│  - State s: [SOC_PROXY, P_solar, eclipse, O_error, m_prop]
│  - Action a: [power_mode, thruster_pulse_duration]    │
│  - Reward r: -(α P_usage + β O_error + γ B_risk + δ F_fuel)
└────────────────────────────────────────────────────────┘
```

---

## 6. Final Status

### READY FOR SIMULATION MODEL DESIGN
