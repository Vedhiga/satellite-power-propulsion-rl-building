import os
import sys
import json
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import SatelliteConfig
from src.envs.satellite_env import UnifiedSatelliteEnv
from src.controllers.rule_based import RuleBasedController
from src.controllers.q_learning import TabularQLearningAgent

class ScenarioEvaluator:
    """
    Monte Carlo Scenario Evaluator for Satellite Control Policies.
    Executes 20-seed Monte Carlo benchmarks across 3 operational stress scenarios:
    1. Nominal Operations
    2. Solar Storm (Degraded solar array generation: 5.5 W peak)
    3. Degraded Bus / Low Battery (Initial SOC 45%, degraded battery capacity: 2.0 Ah)
    """
    def __init__(self, num_seeds: int = 20, num_steps: int = 100):
        self.num_seeds = num_seeds
        self.num_steps = num_steps

        # Define Scenario Configs & Initial Conditions
        self.scenarios = {
            "nominal": {
                "name": "Nominal LEO Operations",
                "config_kwargs": {"P_solar_max": 8.0, "C_bat_Ah": 2.6},
                "init_kwargs": {"initial_altitude": 396.5, "initial_soc": 0.75, "initial_propellant": 1.5}
            },
            "solar_storm": {
                "name": "Solar Storm (Array Degradation)",
                "config_kwargs": {"P_solar_max": 5.5, "C_bat_Ah": 2.6},
                "init_kwargs": {"initial_altitude": 396.5, "initial_soc": 0.65, "initial_propellant": 1.5}
            },
            "degraded_bus": {
                "name": "Degraded Bus (Low Initial SOC & Battery Aging)",
                "config_kwargs": {"P_solar_max": 8.0, "C_bat_Ah": 2.0},
                "init_kwargs": {"initial_altitude": 394.0, "initial_soc": 0.45, "initial_propellant": 1.5}
            }
        }

    def evaluate_controller_on_scenario(self, controller, scenario_key: str) -> dict:
        """
        Runs 20 Monte Carlo evaluation runs for a given controller on a specified scenario.
        """
        sc_info = self.scenarios[scenario_key]
        cfg_kwargs = sc_info["config_kwargs"]
        init_kwargs = sc_info["init_kwargs"]

        rewards = []
        tracking_errors = []
        fuel_expended_g_list = []
        final_socs = []
        survivals = []

        for seed in range(self.num_seeds):
            np.random.seed(seed)

            # Build environment with scenario configuration
            cfg = SatelliteConfig(**cfg_kwargs)
            env = UnifiedSatelliteEnv(config=cfg)

            # Phase offset based on seed to simulate varied orbital injection times
            start_time = float((seed * 300.0) % cfg.orbit_period_s)

            state = env.reset(
                initial_altitude=init_kwargs["initial_altitude"],
                initial_soc=init_kwargs["initial_soc"],
                initial_propellant=init_kwargs["initial_propellant"],
                start_time=start_time
            )

            ep_reward = 0.0
            ep_errors = []
            init_fuel = env.propellant
            survived = True

            for step in range(self.num_steps):
                # Handle controller parameter signature differences safely
                if isinstance(controller, RuleBasedController) or hasattr(controller, "action_map"):
                    action = controller.select_action(env)
                else:
                    action = controller.select_action(state, training=False)

                next_state, reward, done, telem = env.step(action)
                ep_reward += reward
                ep_errors.append(abs(env.altitude - env.cfg.h_target))

                state = next_state
                if done:
                    survived = (step == self.num_steps - 1)
                    break

            rewards.append(ep_reward)
            tracking_errors.append(np.mean(ep_errors))
            fuel_expended_g_list.append((init_fuel - env.propellant) * 1000.0)
            final_socs.append(env.soc * 100.0)
            survivals.append(1.0 if survived else 0.0)

        return {
            "mean_reward": float(np.mean(rewards)),
            "std_reward": float(np.std(rewards)),
            "mean_tracking_error_km": float(np.mean(tracking_errors)),
            "std_tracking_error_km": float(np.std(tracking_errors)),
            "mean_fuel_expended_g": float(np.mean(fuel_expended_g_list)),
            "std_fuel_expended_g": float(np.std(fuel_expended_g_list)),
            "mean_final_soc_pct": float(np.mean(final_socs)),
            "std_final_soc_pct": float(np.std(final_socs)),
            "survival_rate_pct": float(np.mean(survivals) * 100.0)
        }

    def run_full_benchmark(self, q_agent: TabularQLearningAgent, rule_controller: RuleBasedController) -> dict:
        """
        Executes comparative Monte Carlo evaluation across all scenarios.
        """
        results = {}
        controllers = {
            "RuleBasedController": rule_controller,
            "TabularQLearningAgent": q_agent
        }

        for sc_key, sc_info in self.scenarios.items():
            results[sc_key] = {
                "scenario_name": sc_info["name"]
            }
            for ctrl_name, ctrl in controllers.items():
                results[sc_key][ctrl_name] = self.evaluate_controller_on_scenario(ctrl, sc_key)

        return results
