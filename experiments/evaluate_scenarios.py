import numpy as np
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ScenarioProfile:
    name: str
    description: str
    drag_multiplier: float
    initial_soc_range: tuple
    initial_alt_range: tuple
    propellant_kg: float

SCENARIOS = {
    "nominal": ScenarioProfile(
        name="Nominal Environmental Profile",
        description="Standard upper-thermospheric density with nominal orbit entry.",
        drag_multiplier=1.0,
        initial_soc_range=(0.70, 0.85),
        initial_alt_range=(396.0, 401.0),
        propellant_kg=1.5
    ),
    "solar_storm": ScenarioProfile(
        name="Solar Maximum Storm Profile",
        description="Severe thermospheric expansion: atmospheric density increased by 200%.",
        drag_multiplier=3.0,
        initial_soc_range=(0.60, 0.80),
        initial_alt_range=(394.0, 398.0),
        propellant_kg=1.5
    ),
    "degraded_bus": ScenarioProfile(
        name="Degraded System Profile",
        description="Aged battery pack and low initial propellant reserve.",
        drag_multiplier=1.0,
        initial_soc_range=(0.35, 0.50),
        initial_alt_range=(395.0, 399.0),
        propellant_kg=0.25
    )
}

class ScenarioEvaluator:
    def __init__(self, env_class, num_seeds: int = 20, steps_per_seed: int = 100):
        self.env_class = env_class
        self.num_seeds = num_seeds
        self.steps_per_seed = steps_per_seed

    def evaluate_controller(self, controller, scenario: ScenarioProfile, is_rl: bool = False) -> Dict[str, Any]:
        rewards, alt_errors, fuel_spent, battery_violations, brownouts = [], [], [], [], []

        for seed in range(self.num_seeds):
            np.random.seed(1000 + seed)
            env = self.env_class()
            
            env.cfg.Cd_A = (2.2 * 0.04) * scenario.drag_multiplier
            init_alt = float(np.random.uniform(*scenario.initial_alt_range))
            init_soc = float(np.random.uniform(*scenario.initial_soc_range))
            init_prop = float(scenario.propellant_kg)
            
            state = env.reset(initial_altitude=init_alt, initial_soc=init_soc, initial_propellant=init_prop)
            
            ep_reward = 0.0
            ep_alt_err = []
            ep_violations = 0
            start_fuel = env.propellant
            
            for t in range(self.steps_per_seed):
                if is_rl:
                    action = controller.select_action(state, training=False)
                else:
                    orbit_phase = (env.time % env.cfg.orbit_period_s) / env.cfg.orbit_period_s
                    is_sun = 0.0 if orbit_phase < env.cfg.eclipse_fraction else 1.0
                    action = controller.select_action(env.altitude, env.soc, is_sun)

                next_state, reward, done, telem = env.step(action)
                ep_reward += reward
                ep_alt_err.append(abs(env.altitude - env.cfg.h_target))
                
                if env.soc < 0.20:
                    ep_violations += 1
                    
                state = next_state
                if done:
                    break

            rewards.append(ep_reward)
            alt_errors.append(float(np.mean(ep_alt_err)))
            fuel_spent.append(float((start_fuel - env.propellant) * 1000.0))
            battery_violations.append(ep_violations)
            brownouts.append(1 if env.soc < 0.15 else 0)

        return {
            "scenario": scenario.name,
            "mean_reward": float(np.mean(rewards)),
            "std_reward": float(np.std(rewards)),
            "mean_alt_error_km": float(np.mean(alt_errors)),
            "mean_fuel_spent_g": float(np.mean(fuel_spent)),
            "total_battery_violations": int(np.sum(battery_violations)),
            "brownout_failure_rate": float(np.mean(brownouts))
        }
