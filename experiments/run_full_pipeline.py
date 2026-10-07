import os
import sys
import json
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.envs.satellite_env import UnifiedSatelliteEnv
from src.controllers.rule_based import RuleBasedController
from src.controllers.q_learning import TabularQLearningAgent
from experiments.evaluate_scenarios import ScenarioEvaluator

def run_full_pipeline(num_episodes: int = 500, num_eval_seeds: int = 20):
    """
    End-to-End Driver Script:
    1. Trains Tabular Q-Learning Agent over 500 episodes in UnifiedSatelliteEnv.
    2. Exports trained Q-table to results/trained_q_table.npy.
    3. Runs 20-seed Monte Carlo comparative benchmark vs RuleBasedController across 3 stress scenarios.
    4. Prints formatted evaluation summary table and exports results to JSON.
    """
    print("================================================================================")
    print("  MULTI-OBJECTIVE SATELLITE CONTROL: TABULAR Q-LEARNING TRAINING & BENCHMARK  ")
    print("================================================================================\n")

    # 1. Environment & Agent Initialization
    env = UnifiedSatelliteEnv()
    agent = TabularQLearningAgent(
        num_states=120,
        num_actions=9,
        alpha=0.10,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.992,
        epsilon_min=0.01
    )

    print(f"Agent Architecture: Tabular Q-Learning (120 States, 9 Actions)")
    print(f"Hyperparameters   : alpha={agent.alpha}, gamma={agent.gamma}, eps_decay={agent.epsilon_decay}")
    print(f"Training Duration : {num_episodes} Episodes (100 steps/episode max)\n")
    print("-" * 80)
    print(f"{'Episode':<8} | {'Epsilon':<8} | {'Total Reward':<13} | {'Final Alt (km)':<15} | {'Final SOC (%)':<13} | {'Steps':<6}")
    print("-" * 80)

    # 2. Q-Learning Training Loop
    np.random.seed(42)
    training_rewards = []

    for ep in range(1, num_episodes + 1):
        # Randomize initial conditions slightly during training to improve generalization
        init_alt = float(np.random.uniform(393.0, 402.0))
        init_soc = float(np.random.uniform(0.40, 0.90))
        start_time = float(np.random.uniform(0.0, env.cfg.orbit_period_s))

        state = env.reset(
            initial_altitude=init_alt,
            initial_soc=init_soc,
            initial_propellant=1.5,
            start_time=start_time
        )

        ep_reward = 0.0
        step_count = 0

        for step in range(100):
            action = agent.select_action(state, training=True)
            next_state, reward, done, telem = env.step(action)

            agent.update(state, action, reward, next_state, done)
            ep_reward += reward
            step_count += 1
            state = next_state

            if done:
                break

        agent.decay_epsilon()
        training_rewards.append(ep_reward)

        if ep == 1 or ep % 50 == 0 or ep == num_episodes:
            print(f"{ep:<8} | {agent.epsilon:<8.4f} | {ep_reward:<13.4f} | {env.altitude:<15.2f} | {env.soc*100:<13.2f} | {step_count:<6}")

    print("-" * 80)
    print(f"Training Complete! Mean Reward over last 100 episodes: {np.mean(training_rewards[-100:]):.4f}\n")

    # 3. Save Trained Q-Table
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    results_dir = os.path.join(proj_root, "results")
    data_results_dir = os.path.join(proj_root, "data", "results")

    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(data_results_dir, exist_ok=True)

    q_table_path = os.path.join(results_dir, "trained_q_table.npy")
    data_q_table_path = os.path.join(data_results_dir, "trained_q_table.npy")

    agent.save_q_table(q_table_path)
    agent.save_q_table(data_q_table_path)

    print(f"Saved Q-Table array to:\n  - {q_table_path}\n  - {data_q_table_path}\n")

    # 4. Comparative Scenario Evaluation
    print("================================================================================")
    print("        MONTE CARLO SCENARIO BENCHMARK (20 SEEDS / SCENARIO x 3 SCENARIOS)      ")
    print("================================================================================")

    evaluator = ScenarioEvaluator(num_seeds=num_eval_seeds, num_steps=100)
    rule_controller = RuleBasedController()

    benchmark_data = evaluator.run_full_benchmark(agent, rule_controller)

    # 5. Print Summary Benchmark Table
    print("\n" + "=" * 105)
    print(f"{'Scenario':<30} | {'Controller':<23} | {'Mean Reward':<12} | {'Alt Err (km)':<12} | {'Fuel (g)':<10} | {'Survival':<9}")
    print("=" * 105)

    for sc_key, sc_res in benchmark_data.items():
        sc_name = sc_res["scenario_name"]
        for ctrl_name in ["RuleBasedController", "TabularQLearningAgent"]:
            m = sc_res[ctrl_name]
            ctrl_disp = "Rule-Based" if ctrl_name == "RuleBasedController" else "Q-Learning"
            print(f"{sc_name:<30} | {ctrl_disp:<23} | {m['mean_reward']:<12.4f} | {m['mean_tracking_error_km']:<12.4f} | {m['mean_fuel_expended_g']:<10.3f} | {m['survival_rate_pct']:<8.1f}%")
        print("-" * 105)

    # 6. Save Final Benchmark Summary JSON
    summary_json_path = os.path.join(results_dir, "final_benchmark_summary.json")
    data_summary_json_path = os.path.join(data_results_dir, "final_benchmark_summary.json")

    summary_export = {
        "training_metadata": {
            "num_episodes": num_episodes,
            "final_epsilon": agent.epsilon,
            "mean_last_100_reward": float(np.mean(training_rewards[-100:]))
        },
        "benchmark_results": benchmark_data
    }

    with open(summary_json_path, "w") as f:
        json.dump(summary_export, f, indent=2)
    with open(data_summary_json_path, "w") as f:
        json.dump(summary_export, f, indent=2)

    print(f"\nSaved benchmark results to:\n  - {summary_json_path}\n  - {data_summary_json_path}\n")
    return summary_export

if __name__ == "__main__":
    run_full_pipeline()
