import os
import numpy as np

class TabularQLearningAgent:
    """
    Tabular Q-Learning Agent for Multi-Objective Autonomous Satellite Control.
    Operates over a discretized 120-state MDP with 9 discrete power-propulsion action pairs.
    """
    def __init__(
        self,
        num_states: int = 120,
        num_actions: int = 9,
        alpha: float = 0.10,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.992,
        epsilon_min: float = 0.01
    ):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.epsilon_decay = float(epsilon_decay)
        self.epsilon_min = float(epsilon_min)

        # Initialize Q-table to zeros
        self.q_table = np.zeros((self.num_states, self.num_actions), dtype=np.float64)

    def select_action(self, state: int, training: bool = True) -> int:
        """
        Selects discrete action index using Epsilon-Greedy policy during training,
        or pure Greedy policy during evaluation.
        """
        state = int(state)
        if training and np.random.rand() < self.epsilon:
            return int(np.random.randint(0, self.num_actions))

        q_values = self.q_table[state]
        max_q = np.max(q_values)
        best_actions = np.where(q_values == max_q)[0]
        return int(np.random.choice(best_actions))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool) -> float:
        """
        Updates Q-table value using standard Temporal Difference (TD) Bellman Equation:
        Q(s, a) <- Q(s, a) + alpha * [r + gamma * max_a' Q(s', a') * (1 - done) - Q(s, a)]
        """
        state = int(state)
        action = int(action)
        next_state = int(next_state)

        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state]) if not done else 0.0
        td_target = reward + (self.gamma * max_next_q)
        td_error = td_target - current_q

        self.q_table[state, action] += self.alpha * td_error
        return float(td_error)

    def decay_epsilon(self) -> float:
        """
        Decays exploration rate epsilon exponentially until epsilon_min threshold.
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return self.epsilon

    def save_q_table(self, filepath: str):
        """
        Saves Q-table numpy array to disk.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        np.save(filepath, self.q_table)

    def load_q_table(self, filepath: str):
        """
        Loads Q-table numpy array from disk.
        """
        self.q_table = np.load(filepath)
