import numpy as np
from src.config import SatelliteConfig

class PropulsionSubsystem:
    """
    Subsystem model for chemical reaction control thruster (RCT) propulsion.
    Calculates propellant mass expulsion m_used, velocity change delta_v,
    and solenoid valve power draw P_valve_draw.
    """
    def __init__(self, config: SatelliteConfig):
        self.cfg = config
        self.thrust_N = self.cfg.mdot * self.cfg.g0 * self.cfg.Isp

    def compute_burn(self, burn_duration_s: float, current_propellant_kg: float, current_total_mass_kg: float):
        """
        Executes thruster burn computation for a given commanded burn duration.

        Returns:
            m_used (float): Expended propellant mass in kg.
            new_propellant (float): Remaining propellant mass in kg.
            new_total_mass (float): Updated spacecraft total mass in kg.
            delta_v (float): Delta-V imparted in m/s.
            P_valve_draw (float): Equivalent average power draw of thruster valves over timestep dt.
            actual_burn_duration (float): Actual executed burn duration bounded by timestep and available fuel.
        """
        burn_duration = max(0.0, min(burn_duration_s, self.cfg.dt))
        if current_propellant_kg <= 0.0:
            burn_duration = 0.0

        m_used = min(self.cfg.mdot * burn_duration, current_propellant_kg)
        new_propellant = max(0.0, current_propellant_kg - m_used)
        new_total_mass = self.cfg.dry_mass + new_propellant

        delta_v = (self.thrust_N * burn_duration) / new_total_mass if new_total_mass > 0 else 0.0
        P_valve_draw = (self.cfg.P_valves * burn_duration) / self.cfg.dt

        return m_used, new_propellant, new_total_mass, delta_v, P_valve_draw, burn_duration
