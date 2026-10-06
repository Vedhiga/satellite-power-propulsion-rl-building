import numpy as np
from dataclasses import dataclass
import sys

@dataclass
class SatelliteConfig:
    # Simulation Timing
    dt: float = 60.0                     # seconds per step

    # Orbital Parameters (LEO Baseline)
    mu: float = 398600.4418            # km^3/s^2
    R_E: float = 6378.137              # km
    h_target: float = 400.0            # km
    h_tolerance: float = 2.0           # km
    rho_0: float = 2.7e-12             # kg/m^3 (reference at 400 km)
    h_0: float = 400.0                 # km
    scale_height: float = 50.0         # km
    Cd_A: float = 2.2 * 0.04           # m^2 (Cd * Drag Area)

    # Propulsion Parameters (STFT Calibrated Envelope)
    g0: float = 9.80665                # m/s^2
    Isp: float = 225.0                 # seconds
    mdot: float = 0.00045              # kg/s (~0.45 g/s)
    P_valves: float = 4.0              # Watts

    # Power & Battery Parameters (BIRDS-3 / SolAero Envelope)
    V_bat: float = 4.10                # Volts
    C_bat_Ah: float = 2.6              # Amp-hours
    P_solar_max: float = 8.0           # Watts
    orbit_period_s: float = 92.5 * 60.0
    eclipse_fraction: float = 0.35

    # Spacecraft Mass Budget
    dry_mass: float = 10.5             # kg
    initial_propellant: float = 1.5    # kg

class UnifiedSatelliteEnv:
    def __init__(self, config: SatelliteConfig = None):
        self.cfg = config if config is not None else SatelliteConfig()
        self.C_bat_coulombs = self.cfg.C_bat_Ah * 3600.0
        self.thrust_N = self.cfg.mdot * self.cfg.g0 * self.cfg.Isp
        self.load_profiles = {0: 2.0, 1: 5.0, 2: 12.0}  # 0: Safe, 1: Standard, 2: Payload

        # 9 Discrete actions: (power_mode, burn_duration_s)
        self.action_table = [
            (0, 0.0), (0, 2.0), (0, 10.0),
            (1, 0.0), (1, 2.0), (1, 10.0),
            (2, 0.0), (2, 2.0), (2, 10.0)
        ]
        self.reset()

    def reset(self, initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0):
        self.time = float(start_time)
        self.altitude = float(initial_altitude)
        self.propellant = float(initial_propellant)
        self.soc = float(initial_soc)
        return self._get_discrete_state()

    def _get_discrete_state(self):
        # 1. Altitude bins (5)
        diff = self.altitude - self.cfg.h_target
        if diff < -10.0:     s_alt = 0
        elif diff < -2.0:    s_alt = 1
        elif diff <= 2.0:    s_alt = 2
        elif diff <= 10.0:   s_alt = 3
        else:                s_alt = 4

        # 2. Battery bins (4)
        if self.soc < 0.20:   s_soc = 0
        elif self.soc < 0.40: s_soc = 1
        elif self.soc < 0.80: s_soc = 2
        else:                 s_soc = 3

        # 3. Propellant bins (3)
        fuel_ratio = self.propellant / self.cfg.initial_propellant if self.cfg.initial_propellant > 0 else 0.0
        if fuel_ratio < 0.25:   s_fuel = 0
        elif fuel_ratio < 0.60: s_fuel = 1
        else:                   s_fuel = 2

        # 4. Illumination bin (2)
        orbit_phase = (self.time % self.cfg.orbit_period_s) / self.cfg.orbit_period_s
        is_sun = 0 if orbit_phase < self.cfg.eclipse_fraction else 1

        flat_idx = (s_alt * 24) + (s_soc * 6) + (s_fuel * 2) + is_sun
        return int(np.clip(flat_idx, 0, 119))

    def step(self, action_idx):
        power_mode, burn_duration = self.action_table[action_idx]
        total_mass = self.cfg.dry_mass + self.propellant
        
        # 1. Propulsion Update
        burn_duration = max(0.0, min(burn_duration, self.cfg.dt))
        if self.propellant <= 0.0:
            burn_duration = 0.0
            
        m_used = min(self.cfg.mdot * burn_duration, self.propellant)
        self.propellant = max(0.0, self.propellant - m_used)
        total_mass = self.cfg.dry_mass + self.propellant
        
        delta_v = (self.thrust_N * burn_duration) / total_mass if total_mass > 0 else 0.0
        P_valve_draw = (self.cfg.P_valves * burn_duration) / self.cfg.dt
        
        # 2. Orbital Mechanics Update
        r_km = self.cfg.R_E + self.altitude
        v_orb_ms = np.sqrt((self.cfg.mu * 1e9) / (r_km * 1000.0))
        delta_h = self.altitude - self.cfg.h_0
        rho = self.cfg.rho_0 * np.exp(-delta_h / self.cfg.scale_height)
        
        da_dt_m = -rho * np.sqrt(self.cfg.mu * 1e9 * r_km * 1000.0) * (self.cfg.Cd_A / total_mass)
        decay_km = (da_dt_m / 1000.0) * self.cfg.dt
        boost_km = (2.0 * r_km / (v_orb_ms / 1000.0)) * (delta_v / 1000.0)
        
        prev_alt = self.altitude
        self.altitude += (decay_km + boost_km)
        
        # 3. Electrical Power System Update
        orbit_phase = (self.time % self.cfg.orbit_period_s) / self.cfg.orbit_period_s
        in_sun = 0.0 if orbit_phase < self.cfg.eclipse_fraction else 1.0
        P_gen = self.cfg.P_solar_max if in_sun == 1.0 else 0.0
        
        P_base = self.load_profiles.get(power_mode, 5.0)
        P_bus = P_base + P_valve_draw
        P_net = P_gen - P_bus
        
        delta_soc = (P_net * self.cfg.dt) / (self.cfg.V_bat * self.C_bat_coulombs)
        prev_soc = self.soc
        self.soc = float(np.clip(self.soc + delta_soc, 0.0, 1.0))
        
        self.time += self.cfg.dt
        
        # 4. Multi-Objective Cost & Reward
        norm_orbit_err = abs(self.altitude - self.cfg.h_target) / self.cfg.h_tolerance
        norm_fuel_used = m_used / (self.cfg.mdot * 10.0)
        norm_power_bus = P_bus / 12.67
        batt_penalty = 10.0 if self.soc < 0.20 else (
            ((0.40 - self.soc) / 0.20)**2 if self.soc < 0.40 else 0.0
        )
        
        cost = (0.4 * norm_orbit_err) + (0.3 * norm_fuel_used) + \
               (0.1 * norm_power_bus) + (0.2 * batt_penalty)
        reward = -cost
        
        done = bool(self.soc < 0.15 or self.altitude < 350.0)
        
        telemetry = {
            "decay_km": decay_km,
            "boost_km": boost_km,
            "net_alt_change_km": self.altitude - prev_alt,
            "delta_soc": self.soc - prev_soc,
            "P_gen": P_gen,
            "P_bus": P_bus,
            "P_net": P_net,
            "m_used_g": m_used * 1000.0,
            "batt_penalty": batt_penalty,
            "burn_duration_s": burn_duration
        }
        return self._get_discrete_state(), reward, done, telemetry

def run_tests():
    env = UnifiedSatelliteEnv()
    test_results = []

    print("================================================================================")
    print("      AUTOMATED TEST SUITE FOR UNIFIED SATELLITE ENVIRONMENT VALIDATION        ")
    print("================================================================================\n")

    # -------------------------------------------------------------------------
    # TEST 1: Propulsion-to-Orbit Mechanics
    # -------------------------------------------------------------------------
    print("--- RUNNING TEST 1: Propulsion-to-Orbit Mechanics ---")
    
    # Idle Step: Action 3 (Standard Mode, 0 s Burn)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    s_idle, r_idle, d_idle, telem_idle = env.step(3)
    
    # Firing Step: Action 5 (Standard Mode, 10 s Burn)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    s_burn, r_burn, d_burn, telem_burn = env.step(5)

    print(f"  Idle Command (Action 3): m_used = {telem_idle['m_used_g']:.4f} g, boost = {telem_idle['boost_km']:.6f} km, decay = {telem_idle['decay_km']:.6f} km, net_alt = {telem_idle['net_alt_change_km']:.6f} km")
    print(f"  Burn Command (Action 5): m_used = {telem_burn['m_used_g']:.4f} g, boost = {telem_burn['boost_km']:.6f} km, decay = {telem_burn['decay_km']:.6f} km, net_alt = {telem_burn['net_alt_change_km']:.6f} km")

    a1_1 = telem_idle['m_used_g'] == 0.0
    a1_2 = telem_idle['boost_km'] == 0.0
    a1_3 = telem_idle['decay_km'] < 0.0
    a1_4 = np.isclose(telem_burn['m_used_g'], 4.5, atol=1e-5)
    a1_5 = telem_burn['boost_km'] > 1.0

    t1_passed = a1_1 and a1_2 and a1_3 and a1_4 and a1_5
    print(f"  Assertions: [m_idle==0: {a1_1}], [boost_idle==0: {a1_2}], [decay_idle<0: {a1_3}], [m_burn==4.5g: {a1_4}], [boost_burn>1km: {a1_5}]")
    print(f"  --> TEST 1 STATUS: {'PASSED' if t1_passed else 'FAILED'}\n")

    test_results.append({
        "id": "TEST-1",
        "name": "Propulsion-to-Orbit Mechanics",
        "hypothesis": "Idle produces zero mass loss & boost with drag decay; 10s burn consumes 4.5g fuel & boosts >1.0 km.",
        "measured": f"Idle m={telem_idle['m_used_g']:.1f}g, boost={telem_idle['boost_km']:.3f}km; Burn m={telem_burn['m_used_g']:.1f}g, boost={telem_burn['boost_km']:.3f}km",
        "status": "PASSED" if t1_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # TEST 2: Solar Generation and Energy Balance
    # -------------------------------------------------------------------------
    print("--- RUNNING TEST 2: Solar Generation and Energy Balance ---")
    
    # Eclipse Step (start_time = 0.0 s)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, _, telem_eclipse = env.step(3)

    # Direct Sunlight Step (start_time = 3000.0 s)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=3000.0)
    _, _, _, telem_sun = env.step(3)

    print(f"  Eclipse (t=0s): P_gen = {telem_eclipse['P_gen']:.2f} W, P_bus = {telem_eclipse['P_bus']:.2f} W, P_net = {telem_eclipse['P_net']:.2f} W, delta_soc = {telem_eclipse['delta_soc']:.6f}")
    print(f"  Sunlight (t=3000s): P_gen = {telem_sun['P_gen']:.2f} W, P_bus = {telem_sun['P_bus']:.2f} W, P_net = {telem_sun['P_net']:.2f} W, delta_soc = {telem_sun['delta_soc']:.6f}")

    a2_1 = telem_eclipse['P_gen'] == 0.0
    a2_2 = telem_eclipse['delta_soc'] < 0.0
    a2_3 = telem_sun['P_gen'] == 8.0
    a2_4 = telem_sun['delta_soc'] > 0.0

    t2_passed = a2_1 and a2_2 and a2_3 and a2_4
    print(f"  Assertions: [P_gen_eclipse==0: {a2_1}], [delta_soc_eclipse<0: {a2_2}], [P_gen_sun==8: {a2_3}], [delta_soc_sun>0: {a2_4}]")
    print(f"  --> TEST 2 STATUS: {'PASSED' if t2_passed else 'FAILED'}\n")

    test_results.append({
        "id": "TEST-2",
        "name": "Solar Generation and Energy Balance",
        "hypothesis": "In eclipse P_gen=0W & SOC drains; in sunlight P_gen=8W > P_bus(5W) & SOC charges.",
        "measured": f"Eclipse P_gen={telem_eclipse['P_gen']:.1f}W, dSOC={telem_eclipse['delta_soc']:.5f}; Sun P_gen={telem_sun['P_gen']:.1f}W, dSOC={+telem_sun['delta_soc']:.5f}",
        "status": "PASSED" if t2_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # TEST 3: Subsystem Cross-Coupling via P_valve and Safety Penalties
    # -------------------------------------------------------------------------
    print("--- RUNNING TEST 3: Subsystem Cross-Coupling via P_valve & Safety Penalties ---")
    
    # Stress Step: Initial SOC = 0.215 (marginal battery charge so step drops SOC below 0.20), Action 8 (Payload mode 2, 10s burn) in eclipse
    env.reset(initial_altitude=400.0, initial_soc=0.215, initial_propellant=1.5, start_time=0.0)
    s_stress, r_stress, d_stress, telem_stress = env.step(8)

    print(f"  Payload+10s Burn in Eclipse: P_base = 12.0W, P_valve = 0.667W -> P_bus = {telem_stress['P_bus']:.4f} W")
    print(f"  SOC Before = 0.2150 -> SOC After = {env.soc:.6f} (< 0.20)")
    print(f"  Battery Penalty = {telem_stress['batt_penalty']:.2f}")

    a3_1 = np.isclose(telem_stress['P_bus'], 12.667, atol=1e-3)
    a3_2 = env.soc < 0.20
    a3_3 = telem_stress['batt_penalty'] == 10.0

    t3_passed = a3_1 and a3_2 and a3_3
    print(f"  Assertions: [P_bus==12.667W: {a3_1}], [SOC<0.20: {a3_2}], [batt_penalty==10.0: {a3_3}]")
    print(f"  --> TEST 3 STATUS: {'PASSED' if t3_passed else 'FAILED'}\n")

    test_results.append({
        "id": "TEST-3",
        "name": "Subsystem Cross-Coupling & Safety Penalties",
        "hypothesis": "Payload + 10s burn draws 12.667 W; pulling marginal SOC (<0.20) triggers maximum penalty 10.0.",
        "measured": f"P_bus={telem_stress['P_bus']:.3f}W, final SOC={env.soc:.4f}, batt_penalty={telem_stress['batt_penalty']:.1f}",
        "status": "PASSED" if t3_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # EDGE CASE A: Propellant Depletion
    # -------------------------------------------------------------------------
    print("--- RUNNING EDGE CASE A: Propellant Depletion ---")
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=0.0, start_time=0.0)
    _, _, _, telem_dep = env.step(5) # Action 5 requests 10s burn

    print(f"  Requested 10s burn with 0.0kg propellant:")
    print(f"  Executed burn_duration = {telem_dep['burn_duration_s']:.2f} s, m_used = {telem_dep['m_used_g']:.4f} g, boost = {telem_dep['boost_km']:.6f} km, propellant = {env.propellant:.4f} kg")

    ea_1 = telem_dep['burn_duration_s'] == 0.0
    ea_2 = telem_dep['m_used_g'] == 0.0
    ea_3 = telem_dep['boost_km'] == 0.0
    ea_4 = env.propellant == 0.0

    edge_a_passed = ea_1 and ea_2 and ea_3 and ea_4
    print(f"  Assertions: [burn_duration==0: {ea_1}], [m_used==0: {ea_2}], [boost==0: {ea_3}], [propellant==0: {ea_4}]")
    print(f"  --> EDGE CASE A STATUS: {'PASSED' if edge_a_passed else 'FAILED'}\n")

    test_results.append({
        "id": "EDGE-A",
        "name": "Propellant Depletion",
        "hypothesis": "With 0.0 kg propellant, requested 10s burn is forced to 0s, 0g used, 0km boost.",
        "measured": f"burn_dur={telem_dep['burn_duration_s']:.1f}s, m_used={telem_dep['m_used_g']:.1f}g, boost={telem_dep['boost_km']:.1f}km",
        "status": "PASSED" if edge_a_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # EDGE CASE B: Battery Overcharge Saturation
    # -------------------------------------------------------------------------
    print("--- RUNNING EDGE CASE B: Battery Overcharge Saturation ---")
    env.reset(initial_altitude=400.0, initial_soc=1.0, initial_propellant=1.5, start_time=3000.0)
    _, _, _, telem_sat = env.step(0) # Safe mode in sunlight: P_gen = 8W, P_bus = 2W -> P_net = +6W

    print(f"  Initial SOC = 1.0, P_net = {telem_sat['P_net']:.2f} W -> Calculated dSOC_raw = {telem_sat['delta_soc']:.6f}")
    print(f"  Final SOC = {env.soc:.6f}")

    eb_1 = env.soc == 1.0
    eb_2 = not np.isnan(env.soc)
    eb_3 = not np.isinf(env.soc)

    edge_b_passed = eb_1 and eb_2 and eb_3
    print(f"  Assertions: [SOC==1.0: {eb_1}], [not NaN: {eb_2}], [not Inf: {eb_3}]")
    print(f"  --> EDGE CASE B STATUS: {'PASSED' if edge_b_passed else 'FAILED'}\n")

    test_results.append({
        "id": "EDGE-B",
        "name": "Battery Overcharge Saturation",
        "hypothesis": "With SOC=1.0 under positive net power generation, SOC remains capped at exactly 1.0 without overflow.",
        "measured": f"Initial SOC=1.0, P_net=+6.0W -> Final SOC={env.soc:.1f}",
        "status": "PASSED" if edge_b_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # EDGE CASE C: Terminal Brownout Condition
    # -------------------------------------------------------------------------
    print("--- RUNNING EDGE CASE C: Terminal Brownout Condition ---")
    env.reset(initial_altitude=400.0, initial_soc=0.151, initial_propellant=1.5, start_time=0.0)
    _, _, done_brown, telem_brown = env.step(8) # High load in eclipse

    print(f"  Initial SOC = 0.1510 -> Final SOC = {env.soc:.6f} (< 0.15) -> done = {done_brown}")

    ec_1 = env.soc < 0.15
    ec_2 = done_brown == True

    edge_c_passed = ec_1 and ec_2
    print(f"  Assertions: [SOC<0.15: {ec_1}], [done==True: {ec_2}]")
    print(f"  --> EDGE CASE C STATUS: {'PASSED' if edge_c_passed else 'FAILED'}\n")

    test_results.append({
        "id": "EDGE-C",
        "name": "Terminal Brownout Condition",
        "hypothesis": "When SOC falls below 0.15, environment terminates with done=True.",
        "measured": f"Final SOC={env.soc:.4f}, done={done_brown}",
        "status": "PASSED" if edge_c_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # EDGE CASE D: Terminal Orbital Re-entry Condition
    # -------------------------------------------------------------------------
    print("--- RUNNING EDGE CASE D: Terminal Orbital Re-entry Condition ---")
    env.reset(initial_altitude=349.9, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, done_decay, telem_decay = env.step(3)

    print(f"  Initial Altitude = 349.90 km -> Final Altitude = {env.altitude:.4f} km (< 350.0 km) -> done = {done_decay}")

    ed_1 = env.altitude < 350.0
    ed_2 = done_decay == True

    edge_d_passed = ed_1 and ed_2
    print(f"  Assertions: [altitude<350km: {ed_1}], [done==True: {ed_2}]")
    print(f"  --> EDGE CASE D STATUS: {'PASSED' if edge_d_passed else 'FAILED'}\n")

    test_results.append({
        "id": "EDGE-D",
        "name": "Terminal Orbital Re-entry",
        "hypothesis": "When altitude falls below 350.0 km, environment terminates with done=True.",
        "measured": f"Final altitude={env.altitude:.2f}km, done={done_decay}",
        "status": "PASSED" if edge_d_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # EDGE CASE E: Discrete State Space Index Invariant
    # -------------------------------------------------------------------------
    print("--- RUNNING EDGE CASE E: Discrete State Space Index Invariant ---")
    altitudes = [300.0, 388.0, 399.0, 401.0, 409.0, 500.0]
    socs = [0.0, 0.15, 0.35, 0.75, 0.95, 1.0]
    fuels = [0.0, 0.3, 0.8, 1.5]
    start_times = [0.0, 3000.0]

    valid_indices = True
    min_idx, max_idx = 999, -1
    count_tested = 0

    for a in altitudes:
        for s in socs:
            for f in fuels:
                for t in start_times:
                    idx = env.reset(initial_altitude=a, initial_soc=s, initial_propellant=f, start_time=t)
                    count_tested += 1
                    if idx < min_idx: min_idx = idx
                    if idx > max_idx: max_idx = idx
                    if not (0 <= idx <= 119):
                        valid_indices = False

    print(f"  Swept {count_tested} extreme state combinations:")
    print(f"  Observed discrete index range: [{min_idx}, {max_idx}] (Allowed: [0, 119])")

    ee_1 = valid_indices
    ee_2 = min_idx >= 0
    ee_3 = max_idx <= 119

    edge_e_passed = ee_1 and ee_2 and ee_3
    print(f"  Assertions: [valid_range: {ee_1}], [min>=0: {ee_2}], [max<=119: {ee_3}]")
    print(f"  --> EDGE CASE E STATUS: {'PASSED' if edge_e_passed else 'FAILED'}\n")

    test_results.append({
        "id": "EDGE-E",
        "name": "Discrete State Index Invariant",
        "hypothesis": "Sweeping extreme state bounds produces valid discrete state index s in [0, 119].",
        "measured": f"Swept {count_tested} states -> Min idx={min_idx}, Max idx={max_idx}",
        "status": "PASSED" if edge_e_passed else "FAILED"
    })

    # -------------------------------------------------------------------------
    # SUMMARY RESULTS TABLE
    # -------------------------------------------------------------------------
    print("==========================================================================================================")
    print("                                SUMMARY TEST RESULTS TABLE                                               ")
    print("==========================================================================================================")
    print(f"| {'Test ID':<8} | {'Test Name':<38} | {'Measured Value Summary':<36} | {'Status':<8} |")
    print("|----------|----------------------------------------|--------------------------------------|----------|")
    for tr in test_results:
        print(f"| {tr['id']:<8} | {tr['name']:<38} | {tr['measured']:<36} | {tr['status']:<8} |")
    print("==========================================================================================================")

    all_passed = all(tr['status'] == "PASSED" for tr in test_results)
    print(f"\nOVERALL TEST SUITE VERIFICATION STATUS: {'ALL TESTS PASSED (100% VALIDATED)' if all_passed else 'SOME TESTS FAILED'}\n")

if __name__ == "__main__":
    run_tests()
