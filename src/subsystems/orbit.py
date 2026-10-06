import numpy as np
from src.config import SatelliteConfig

class OrbitDynamics:
    """
    Subsystem model for Low Earth Orbit dynamics.
    Calculates atmospheric drag decay using an exponential scale-height density model
    and orbital altitude boost using the Vis-Viva velocity formulation.
    """
    def __init__(self, config: SatelliteConfig):
        self.cfg = config

    def compute_step(self, altitude_km: float, total_mass_kg: float, delta_v_ms: float):
        """
        Computes one control step of orbital altitude evolution under drag decay and propulsion boost.

        Returns:
            new_altitude (float): Updated orbital altitude in km.
            decay_km (float): Altitude lost to atmospheric drag in km (negative value).
            boost_km (float): Altitude gained from propulsion boost in km (positive value).
        """
        r_km = self.cfg.R_E + altitude_km
        v_orb_ms = np.sqrt((self.cfg.mu * 1e9) / (r_km * 1000.0))
        delta_h = altitude_km - self.cfg.h_0
        rho = self.cfg.rho_0 * np.exp(-delta_h / self.cfg.scale_height)

        da_dt_m = -rho * np.sqrt(self.cfg.mu * 1e9 * r_km * 1000.0) * (self.cfg.Cd_A / total_mass_kg)
        decay_km = (da_dt_m / 1000.0) * self.cfg.dt
        boost_km = (2.0 * r_km / (v_orb_ms / 1000.0)) * (delta_v_ms / 1000.0)

        new_altitude = altitude_km + decay_km + boost_km
        return new_altitude, decay_km, boost_km
