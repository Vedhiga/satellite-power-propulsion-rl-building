import os
import sys
import json
import numpy as np

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.envs.satellite_env import UnifiedSatelliteEnv
from src.controllers.rule_based import RuleBasedController

def run_baseline_experiment():
    """
    Driver script to evaluate the deterministic RuleBasedController baseline
    over 100 simulation steps (~1.6 orbits), outputting performance metrics and trajectory logs.
    """
    env = UnifiedSatelliteEnv()
    controller = RuleBasedController()

    initial_altitude = 396.5
    initial_soc = 0.75
    initial_propellant = 1.5

    state = env.reset(
        initial_altitude=initial_altitude,
        initial_soc=initial_soc,
        initial_propellant=initial_propellant,
        start_time=0.0
    )

    trajectory = []
    cumulative_reward = 0.0
    tracking_errors = []

    print("================================================================================")
    print("      RULE-BASED CONTROLLER BASELINE EVALUATION (100 STEPS ~ 1.6 ORBITS)        ")
    print("================================================================================\n")
    print(f"Initial State: Altitude={initial_altitude} km, SOC={initial_soc*100:.1f}%, Propellant={initial_propellant} kg\n")
    print(f"{'Step':<6} | {'Time (s)':<8} | {'Alt (km)':<9} | {'SOC (%)':<8} | {'Prop (kg)':<10} | {'Mode':<8} | {'Burn (s)':<8} | {'Reward':<9}")
    print("-" * 85)

    num_steps = 100
    for step_idx in range(1, num_steps + 1):
        action_idx = controller.select_action(env)
        power_mode, burn_duration = env.action_table[action_idx]

        next_state, reward, done, telem = env.step(action_idx)
        cumulative_reward += reward

        tracking_err = abs(env.altitude - env.cfg.h_target)
        tracking_errors.append(tracking_err)

        step_log = {
            "step": step_idx,
            "time_s": float(env.time - env.cfg.dt),
            "altitude_km": float(env.altitude),
            "soc_pct": float(env.soc * 100.0),
            "propellant_kg": float(env.propellant),
            "power_mode": int(power_mode),
            "burn_duration_s": float(burn_duration),
            "reward": float(reward),
            "telemetry": {k: float(v) for k, v in telem.items()}
        }
        trajectory.append(step_log)

        if step_idx == 1 or step_idx % 10 == 0 or step_idx == num_steps:
            mode_names = {0: "Safe", 1: "Standard", 2: "Payload"}
            print(f"{step_idx:<6} | {env.time - env.cfg.dt:<8.1f} | {env.altitude:<9.3f} | {env.soc*100:<8.2f} | {env.propellant:<10.4f} | {mode_names[power_mode]:<8} | {burn_duration:<8.1f} | {reward:<9.4f}")

        if done:
            print(f"\nEpisode terminated early at step {step_idx}!")
            break

    mean_tracking_error = float(np.mean(tracking_errors))
    total_propellant_expended_g = float((initial_propellant - env.propellant) * 1000.0)
    final_soc_pct = float(env.soc * 100.0)

    summary_metrics = {
        "num_steps": len(trajectory),
        "cumulative_reward": float(cumulative_reward),
        "mean_tracking_error_km": mean_tracking_error,
        "total_propellant_expended_g": total_propellant_expended_g,
        "final_soc_pct": final_soc_pct,
        "final_altitude_km": float(env.altitude),
        "final_propellant_kg": float(env.propellant)
    }

    print("\n================================================================================")
    print("                      BASELINE EVALUATION SUMMARY METRICS                       ")
    print("================================================================================")
    print(f"  Cumulative Reward            : {cumulative_reward:.4f}")
    print(f"  Mean Tracking Error (km)     : {mean_tracking_error:.4f} km")
    print(f"  Total Propellant Expended (g): {total_propellant_expended_g:.4f} g")
    print(f"  Final Battery SOC (%)        : {final_soc_pct:.2f} %")
    print(f"  Final Altitude (km)          : {env.altitude:.4f} km")
    print("================================================================================\n")

    # Export to data/results/baseline_metrics.json
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "results"))
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "baseline_metrics.json")

    output_data = {
        "summary_metrics": summary_metrics,
        "trajectory": trajectory
    }

    with open(results_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved baseline evaluation metrics to {results_file}\n")
    return summary_metrics

if __name__ == "__main__":
    run_baseline_experiment()
