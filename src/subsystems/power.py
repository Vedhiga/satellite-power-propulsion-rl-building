import numpy as np
from src.config import SatelliteConfig

class PowerSubsystem:
    """
    Subsystem model for Electrical Power System (EPS).
    Calculates eclipse lighting conditions, solar panel generation, bus load power,
    net power balance, and battery State-of-Charge (SOC) integration.
    """
    def __init__(self, config: SatelliteConfig):
        self.cfg = config
        self.C_bat_coulombs = self.cfg.C_bat_Ah * 3600.0
        self.load_profiles = {0: 2.0, 1: 5.0, 2: 12.0}  # 0: Safe (2W), 1: Standard (5W), 2: Payload (12W)

    def compute_step(self, time_s: float, current_soc: float, power_mode: int, P_valve_draw_W: float):
        """
        Computes power generation, bus draw, and battery SOC update for one timestep.

        Returns:
            new_soc (float): Clamped battery State-of-Charge in range [0.0, 1.0].
            delta_soc (float): Change in SOC over the timestep.
            P_gen (float): Solar panel power generation in Watts.
            P_bus (float): Total spacecraft bus power consumption in Watts.
            P_net (float): Net power balance (P_gen - P_bus) in Watts.
            in_sun (float): Illumination indicator (1.0 for sun, 0.0 for eclipse).
        """
        orbit_phase = (time_s % self.cfg.orbit_period_s) / self.cfg.orbit_period_s
        in_sun = 0.0 if orbit_phase < self.cfg.eclipse_fraction else 1.0
        P_gen = self.cfg.P_solar_max if in_sun == 1.0 else 0.0

        P_base = self.load_profiles.get(power_mode, 5.0)
        P_bus = P_base + P_valve_draw_W
        P_net = P_gen - P_bus

        delta_soc = (P_net * self.cfg.dt) / (self.cfg.V_bat * self.C_bat_coulombs)
        new_soc = float(np.clip(current_soc + delta_soc, 0.0, 1.0))

        return new_soc, delta_soc, P_gen, P_bus, P_net, in_sun
