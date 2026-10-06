from dataclasses import dataclass

@dataclass
class SatelliteConfig:
    """
    Physical configuration and parameters for the Small Satellite Power & Propulsion System.
    Calibrated against BIRDS-3 1U/3U CubeSat EPS telemetry and STFT propulsion ground-test datasets.
    """
    # Simulation Timing
    dt: float = 60.0                     # seconds per step (1-minute control timestep)

    # Orbital Parameters (LEO Baseline)
    mu: float = 398600.4418            # km^3/s^2 (Earth gravitational parameter)
    R_E: float = 6378.137              # km (Earth mean equatorial radius)
    h_target: float = 400.0            # km (Target altitude)
    h_tolerance: float = 2.0           # km (Altitude error tolerance band)
    rho_0: float = 2.7e-12             # kg/m^3 (Reference atmospheric density at 400 km)
    h_0: float = 400.0                 # km (Reference atmospheric height)
    scale_height: float = 50.0         # km (Atmospheric scale height)
    Cd_A: float = 2.2 * 0.04           # m^2 (Drag coefficient Cd=2.2 * Cross-sectional area A=0.04 m^2)

    # Propulsion Parameters (STFT Calibrated Envelope)
    g0: float = 9.80665                # m/s^2 (Standard gravitational acceleration)
    Isp: float = 225.0                 # seconds (Monopropellant RCT specific impulse)
    mdot: float = 0.00045              # kg/s (~0.45 g/s mass flow rate)
    P_valves: float = 4.0              # Watts (Solenoid thruster valve power draw)

    # Power & Battery Parameters (BIRDS-3 / SolAero Envelope)
    V_bat: float = 4.10                # Volts (Nominal 1S Li-ion battery voltage)
    C_bat_Ah: float = 2.6              # Amp-hours (Nominal battery capacity)
    P_solar_max: float = 8.0           # Watts (Maximum solar array generation in full sun)
    orbit_period_s: float = 92.5 * 60.0 # seconds (92.5 minute LEO orbital period)
    eclipse_fraction: float = 0.35      # 35% of orbit spent in Earth shadow (umbra)

    # Spacecraft Mass Budget
    dry_mass: float = 10.5             # kg (Spacecraft bus dry mass)
    initial_propellant: float = 1.5    # kg (Initial monopropellant load)
