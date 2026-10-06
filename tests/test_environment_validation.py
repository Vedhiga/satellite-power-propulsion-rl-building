import numpy as np
import pytest
from src.config import SatelliteConfig
from src.envs.satellite_env import UnifiedSatelliteEnv

def test_1_propulsion_to_orbit_mechanics():
    """
    Test 1: Verifies propulsion-to-orbit coupling:
    - Idle command (0s burn) produces zero propellant loss, zero boost, and drag decay (<0 km).
    - Firing command (10s burn) consumes 4.5g fuel and imparts >1.0 km boost.
    """
    env = UnifiedSatelliteEnv()
    
    # Idle command (Action 3: Standard mode, 0s burn)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, _, telem_idle = env.step(3)

    # Burn command (Action 5: Standard mode, 10s burn)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, _, telem_burn = env.step(5)

    assert telem_idle['m_used_g'] == 0.0
    assert telem_idle['boost_km'] == 0.0
    assert telem_idle['decay_km'] < 0.0
    assert np.isclose(telem_burn['m_used_g'], 4.5, atol=1e-5)
    assert telem_burn['boost_km'] > 1.0

def test_2_solar_generation_and_energy_balance():
    """
    Test 2: Verifies EPS solar generation and illumination geometry:
    - Eclipse (t=0s): P_gen = 0.0 W, battery drains (delta_soc < 0).
    - Sunlight (t=3000s): P_gen = 8.0 W > P_bus (5.0 W), battery charges (delta_soc > 0).
    """
    env = UnifiedSatelliteEnv()
    
    # Eclipse step (start_time = 0.0 s)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, _, telem_eclipse = env.step(3)

    # Sunlight step (start_time = 3000.0 s)
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=3000.0)
    _, _, _, telem_sun = env.step(3)

    assert telem_eclipse['P_gen'] == 0.0
    assert telem_eclipse['delta_soc'] < 0.0
    assert telem_sun['P_gen'] == 8.0
    assert telem_sun['delta_soc'] > 0.0

def test_3_subsystem_cross_coupling_and_penalties():
    """
    Test 3: Verifies thruster valve power coupling and nonlinear battery safety penalty:
    - Action 8 (Payload mode 12W + 10s burn 0.667W valve draw) draws 12.667 W total bus power.
    - Pulling marginal battery (initial SOC = 0.215) below 0.20 triggers maximum penalty 10.0.
    """
    env = UnifiedSatelliteEnv()
    env.reset(initial_altitude=400.0, initial_soc=0.215, initial_propellant=1.5, start_time=0.0)
    _, _, _, telem_stress = env.step(8)

    assert np.isclose(telem_stress['P_bus'], 12.667, atol=1e-3)
    assert env.soc < 0.20
    assert telem_stress['batt_penalty'] == 10.0

def test_edge_case_a_propellant_depletion():
    """
    Edge Case A: Propellant Depletion (0.0 kg propellant).
    Requested 10s burn is forced to 0s duration, 0g fuel used, 0km boost.
    """
    env = UnifiedSatelliteEnv()
    env.reset(initial_altitude=400.0, initial_soc=0.85, initial_propellant=0.0, start_time=0.0)
    _, _, _, telem = env.step(5)

    assert telem['burn_duration_s'] == 0.0
    assert telem['m_used_g'] == 0.0
    assert telem['boost_km'] == 0.0
    assert env.propellant == 0.0

def test_edge_case_b_battery_saturation():
    """
    Edge Case B: Battery Overcharge Protection (SOC = 1.0).
    Positive net power generation under initial SOC=1.0 keeps SOC capped at 1.0 without overflow.
    """
    env = UnifiedSatelliteEnv()
    env.reset(initial_altitude=400.0, initial_soc=1.0, initial_propellant=1.5, start_time=3000.0)
    _, _, _, telem = env.step(0)

    assert env.soc == 1.0
    assert not np.isnan(env.soc)
    assert not np.isinf(env.soc)

def test_edge_case_c_terminal_brownout():
    """
    Edge Case C: Terminal Brownout Condition (SOC < 0.15).
    When SOC falls below 0.15, environment terminates with done=True.
    """
    env = UnifiedSatelliteEnv()
    env.reset(initial_altitude=400.0, initial_soc=0.151, initial_propellant=1.5, start_time=0.0)
    _, _, done, _ = env.step(8)

    assert env.soc < 0.15
    assert done is True

def test_edge_case_d_terminal_orbital_reentry():
    """
    Edge Case D: Terminal Orbital Re-entry Condition (altitude < 350.0 km).
    When altitude falls below 350.0 km, environment terminates with done=True.
    """
    env = UnifiedSatelliteEnv()
    env.reset(initial_altitude=349.9, initial_soc=0.85, initial_propellant=1.5, start_time=0.0)
    _, _, done, _ = env.step(3)

    assert env.altitude < 350.0
    assert done is True

def test_edge_case_e_discrete_state_index_invariant():
    """
    Edge Case E: Discrete State Index Invariant (0 <= s <= 119).
    Sweeps extreme state boundaries and verifies index stays within [0, 119].
    """
    env = UnifiedSatelliteEnv()
    altitudes = [300.0, 388.0, 399.0, 401.0, 409.0, 500.0]
    socs = [0.0, 0.15, 0.35, 0.75, 0.95, 1.0]
    fuels = [0.0, 0.3, 0.8, 1.5]
    start_times = [0.0, 3000.0]

    for a in altitudes:
        for s in socs:
            for f in fuels:
                for t in start_times:
                    idx = env.reset(initial_altitude=a, initial_soc=s, initial_propellant=f, start_time=t)
                    assert 0 <= idx <= 119
