import numpy as np
from dataclasses import dataclass

@dataclass
class RewardWeights:
    alpha_power: float = 0.10     # Weight for normalized bus power draw
    beta_orbit: float = 0.40      # Weight for normalized orbital altitude error
    gamma_battery: float = 0.20   # Weight for battery health risk penalty
    delta_fuel: float = 0.30      # Weight for normalized propellant consumption

class MultiObjectiveRewardEvaluator:
    """
    Computes normalized multi-objective operational cost and scalar RL reward.
    Cost: f = alpha*P_norm + beta*O_norm + gamma*B_penalty + delta*F_norm
    Reward: r = -f - R_terminal * Done
    """
    def __init__(self, weights: RewardWeights = None):
        self.w = weights if weights is not None else RewardWeights()
        self.h_target = 400.0         # km
        self.h_tolerance = 2.0        # km (dead-band half-width)
        self.max_bus_power = 12.667   # W (12W payload + 0.667W valve draw)
        self.max_step_fuel_g = 4.5    # g (0.45 g/s * 10 s max burn)

    def evaluate(self, altitude_km: float, soc: float, bus_power_w: float, fuel_used_g: float):
        # 1. Normalized Orbit Tracking Error
        alt_error_km = abs(altitude_km - self.h_target)
        O_norm = alt_error_km / self.h_tolerance

        # 2. Normalized Propellant Consumption
        F_norm = fuel_used_g / self.max_step_fuel_g

        # 3. Normalized Bus Power Load
        P_norm = bus_power_w / self.max_bus_power

        # 4. Non-linear Battery Safety Barrier Penalty
        if soc >= 0.40:
            B_penalty = 0.0
        elif soc >= 0.20:
            B_penalty = ((0.40 - soc) / 0.20) ** 2
        else:
            B_penalty = 10.0

        step_cost = (
            self.w.beta_orbit * O_norm +
            self.w.delta_fuel * F_norm +
            self.w.alpha_power * P_norm +
            self.w.gamma_battery * B_penalty
        )
        
        step_reward = -step_cost
        
        cost_breakdown = {
            "O_norm": O_norm,
            "F_norm": F_norm,
            "P_norm": P_norm,
            "B_penalty": B_penalty,
            "total_cost": step_cost
        }
        return step_reward, cost_breakdown
