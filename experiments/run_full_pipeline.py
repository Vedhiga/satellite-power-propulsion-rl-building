import os
import json
import numpy as np
from src.envs.satellite_env import UnifiedSatelliteEnv
from src.controllers.rule_based import RuleBasedController
from src.controllers.q_learning import TabularQLearningAgent
from experiments.evaluate_scenarios import SCENARIOS, ScenarioEvaluator

def execute_complete_pipeline():
    print("=" * 80)
    print("STARTING END-TO-END REINFORCEMENT LEARNING TRAINING AND EVALUATION PIPELINE")
    print("=" * 80)

    env = UnifiedSatelliteEnv()
    agent = TabularQLearningAgent(
        num_states=120,
        num_actions=9,
        learning_rate=0.10,
        discount_factor=0.95,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.992
    )
    baseline = RuleBasedController(env)

    num_episodes = 500
    max_steps = 100
    print(f"\n[PHASE 1] Continuously Training Tabular Q-Agent over {num_episodes} episodes...")

    episode_rewards = []
    for ep in range(1, num_episodes + 1):
        init_alt = np.random.uniform(395.0, 401.0)
        init_soc = np.random.uniform(0.65, 0.85)
        init_time = float(np.random.choice([0.0, 1500.0, 3000.0]))
        
        state = env.reset(initial_altitude=init_alt, initial_soc=init_soc, start_time=init_time)
        ep_reward = 0.0
        
        for step in range(max_steps):
            action = agent.select_action(state, training=True)
            next_state, reward, done, telem = env.step(action)
            agent.update(state, action, reward, next_state, done)
            ep_reward += reward
            state = next_state
            if done:
                break
                
        agent.decay_exploration()
        episode_rewards.append(ep_reward)
        
        if ep % 50 == 0 or ep == 1:
            recent_avg = np.mean(episode_rewards[-50:])
            print(f"  Episode {ep:3d}/{num_episodes} | Step Reward: {ep_reward:7.2f} | "
                  f"Last 50 Avg: {recent_avg:7.2f} | Epsilon: {agent.epsilon:.3f}")

    os.makedirs("results", exist_ok=True)
    q_table_path = "results/trained_q_table.npy"
    agent.save_policy(q_table_path)
    print(f"\n  --> Training complete. Q-Table saved to: {q_table_path}")

    print("\n[PHASE 2] Executing Monte Carlo Stress Evaluations (20 seeds per scenario)...")
    evaluator = ScenarioEvaluator(env_class=UnifiedSatelliteEnv, num_seeds=20, steps_per_seed=100)
    comparative_results = []
    
    for scenario_key, scenario in SCENARIOS.items():
        print(f"  Evaluating Scenario: {scenario.name}...")
        rl_metrics = evaluator.evaluate_controller(agent, scenario, is_rl=True)
        base_metrics = evaluator.evaluate_controller(baseline, scenario, is_rl=False)
        
        comparative_results.append({
            "scenario": scenario.name,
            "agent": "Tabular Q-Learning",
            "mean_reward": rl_metrics["mean_reward"],
            "alt_err_km": rl_metrics["mean_alt_error_km"],
            "fuel_spent_g": rl_metrics["mean_fuel_spent_g"],
            "batt_violations": rl_metrics["total_battery_violations"],
            "failure_rate": rl_metrics["brownout_failure_rate"]
        })
        
        comparative_results.append({
            "scenario": scenario.name,
            "agent": "Rule-Based Baseline",
            "mean_reward": base_metrics["mean_reward"],
            "alt_err_km": base_metrics["mean_alt_error_km"],
            "fuel_spent_g": base_metrics["mean_fuel_spent_g"],
            "batt_violations": base_metrics["total_battery_violations"],
            "failure_rate": base_metrics["brownout_failure_rate"]
        })

    print("\n" + "=" * 90)
    print("FINAL COMPARATIVE BENCHMARK MATRIX (Q-LEARNING vs. RULE-BASED)")
    print("=" * 90)
    print(f"{'Scenario':<30} | {'Controller':<20} | {'Mean Reward':<11} | {'Alt Err (km)':<12} | {'Fuel (g)':<9} | {'Violations'}")
    print("-" * 90)
    for res in comparative_results:
        print(f"{res['scenario'][:30]:<30} | {res['agent']:<20} | {res['mean_reward']:<11.2f} | {res['alt_err_km']:<12.3f} | {res['fuel_spent_g']:<9.2f} | {res['batt_violations']}")
    print("=" * 90)

    summary_path = "results/final_benchmark_summary.json"
    with open(summary_path, "w") as f:
        json.dump(comparative_results, f, indent=2)
    print(f"  --> Benchmark summary saved to: {summary_path}")

if __name__ == "__main__":
    execute_complete_pipeline()
