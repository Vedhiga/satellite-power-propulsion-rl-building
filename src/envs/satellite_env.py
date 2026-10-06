import numpy as np
from src.config import SatelliteConfig
from src.subsystems.propulsion import PropulsionSubsystem
from src.subsystems.orbit import OrbitDynamics
from src.subsystems.power import PowerSubsystem

class UnifiedSatelliteEnv:
    """
    Unified Satellite Reinforcement Learning Simulation Environment.
    Combines LEO orbital dynamics, propulsion firing envelope, and EPS battery energy balance
    into a discrete multi-objective Markov Decision Process (MDP).
    """
    def __init__(self, config: SatelliteConfig = None):
        self.cfg = config if config is not None else SatelliteConfig()
        self.propulsion = PropulsionSubsystem(self.cfg)
        self.orbit = OrbitDynamics(self.cfg)
        self.power = PowerSubsystem(self.cfg)

        # 9 Discrete actions: (power_mode, burn_duration_s)
        self.action_table = [
            (0, 0.0), (0, 2.0), (0, 10.0),  # Safe Mode (2W)
            (1, 0.0), (1, 2.0), (1, 10.0),  # Standard Mode (5W)
            (2, 0.0), (2, 2.0), (2, 10.0)   # Payload Mode (12W)
        ]
        self.reset()

    def reset(self, initial_altitude=400.0, initial_soc=0.85, initial_propellant=1.5, start_time=0.0):
        """
        Resets environment to specified or default initial conditions.
        Returns initial discrete state index.
        """
        self.time = float(start_time)
        self.altitude = float(initial_altitude)
        self.propellant = float(initial_propellant)
        self.soc = float(initial_soc)
        return self._get_discrete_state()

    def _get_discrete_state(self):
        """
        Discretizes continuous state vector (altitude, SOC, propellant, illumination)
        into a single flat discrete state index s in [0, 119].
        Total state space size: 5 * 4 * 3 * 2 = 120 states.
        """
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

    def step(self, action_idx: int):
        """
        Executes one control step in the satellite simulation.

        Returns:
            next_state (int): Discrete state index.
            reward (float): Scalarized multi-objective reward.
            done (bool): Terminal episode flag.
            telemetry (dict): Step telemetry dictionary.
        """
        power_mode, req_burn_duration = self.action_table[action_idx]
        current_total_mass = self.cfg.dry_mass + self.propellant

        # 1. Propulsion Update
        m_used, self.propellant, current_total_mass, delta_v, P_valve_draw, actual_burn_duration = \
            self.propulsion.compute_burn(req_burn_duration, self.propellant, current_total_mass)

        # 2. Orbital Mechanics Update
        prev_alt = self.altitude
        self.altitude, decay_km, boost_km = self.orbit.compute_step(self.altitude, current_total_mass, delta_v)

        # 3. Electrical Power System Update
        prev_soc = self.soc
        self.soc, delta_soc, P_gen, P_bus, P_net, in_sun = \
            self.power.compute_step(self.time, self.soc, power_mode, P_valve_draw)

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
            "burn_duration_s": actual_burn_duration,
            "in_sun": in_sun
        }
        return self._get_discrete_state(), reward, done, telemetry
