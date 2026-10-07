import numpy as np
from dataclasses import dataclass

@dataclass
class RewardWeights:
    """
    Normalized multi-objective cost function weights for satellite operations:
    - alpha_power: Bus electric power consumption cost weight
    - beta_orbit: Orbital altitude tracking error cost weight
    - gamma_battery: Deep battery discharge risk penalty weight
    - delta_fuel: Monopropellant expenditure cost weight
    """
    alpha_power: float = 0.10     # Weight for normalized bus power draw
    beta_orbit: float = 0.40      # Weight for normalized orbital altitude error
    gamma_battery: float = 0.20   # Weight for battery health risk penalty
    delta_fuel: float = 0.30      # Weight for normalized propellant consumption

class MultiObjectiveRewardEvaluator:
    """
    Computes normalized multi-objective scalar reward and component cost breakdown
    for small-satellite power and station-keeping management.
    """
    def __init__(self, weights: RewardWeights = None):
        self.weights = weights if weights is not None else RewardWeights()

    def compute_battery_penalty(self, soc: float) -> float:
        """
        Computes non-linear penalty for battery State of Charge (SOC):
        - Severe penalty (10.0) if SOC < 0.20 (Terminal Brownout zone)
        - Quadratic penalty scaling if 0.20 <= SOC < 0.40 (Deep Discharge risk)
        - Zero penalty if SOC >= 0.40 (Healthy operational range)
        """
        if soc < 0.20:
            return 10.0
        elif soc < 0.40:
            return float(((0.40 - soc) / 0.20) ** 2)
        return 0.0

    def compute_reward(
        self,
        altitude: float,
        soc: float,
        m_used_kg: float,
        p_bus: float,
        h_target: float = 400.0,
        h_tolerance: float = 2.0
    ) -> float:
        """
        Computes scalarized negative cost reward r in [-inf, 0].
        """
        norm_orbit_err = abs(altitude - h_target) / h_tolerance
        norm_fuel_used = m_used_kg / (0.00045 * 10.0)  # Normalized by max 10s burn fuel mass
        norm_power_bus = p_bus / 12.67                  # Normalized by maximum peak bus power
        batt_penalty = self.compute_battery_penalty(soc)

        cost = (
            (self.weights.beta_orbit * norm_orbit_err) +
            (self.weights.delta_fuel * norm_fuel_used) +
            (self.weights.alpha_power * norm_power_bus) +
            (self.weights.gamma_battery * batt_penalty)
        )
        return float(-cost)

    def evaluate_step(
        self,
        altitude: float,
        soc: float,
        m_used_kg: float,
        p_bus: float,
        h_target: float = 400.0,
        h_tolerance: float = 2.0
    ) -> dict:
        """
        Returns full cost breakdown and resulting reward dictionary.
        """
        norm_orbit_err = abs(altitude - h_target) / h_tolerance
        norm_fuel_used = m_used_kg / (0.00045 * 10.0)
        norm_power_bus = p_bus / 12.67
        batt_penalty = self.compute_battery_penalty(soc)

        cost_orbit = self.weights.beta_orbit * norm_orbit_err
        cost_fuel = self.weights.delta_fuel * norm_fuel_used
        cost_power = self.weights.alpha_power * norm_power_bus
        cost_battery = self.weights.gamma_battery * batt_penalty

        total_cost = cost_orbit + cost_fuel + cost_power + cost_battery
        reward = -total_cost

        return {
            "reward": float(reward),
            "total_cost": float(total_cost),
            "cost_components": {
                "orbit_tracking": float(cost_orbit),
                "propellant_consumption": float(cost_fuel),
                "power_bus_draw": float(cost_power),
                "battery_health": float(cost_battery)
            },
            "normalized_metrics": {
                "norm_orbit_err": float(norm_orbit_err),
                "norm_fuel_used": float(norm_fuel_used),
                "norm_power_bus": float(norm_power_bus),
                "batt_penalty": float(batt_penalty)
            }
        }
