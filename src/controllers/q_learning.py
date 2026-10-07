import numpy as np

class TabularQLearningAgent:
    """
    Autonomous Tabular Q-Learning Agent for Satellite Subsystem Control.
    State space: 120 discrete states
    Action space: 9 discrete actions
    """
    def __init__(
        self,
        num_states: int = 120,
        num_actions: int = 9,
        learning_rate: float = 0.10,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.992
    ):
        self.num_states = num_states
        self.num_actions = num_actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Optimistic initialization with zeros (since r <= 0)
        self.q_table = np.zeros((num_states, num_actions), dtype=np.float64)

    def select_action(self, state: int, training: bool = True) -> int:
        """Epsilon-greedy action selection with unbiased random tie-breaking."""
        if training and np.random.rand() < self.epsilon:
            return int(np.random.randint(self.num_actions))
        
        q_row = self.q_table[state, :]
        max_val = np.max(q_row)
        best_actions = np.where(q_row == max_val)[0]
        return int(np.random.choice(best_actions))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool) -> float:
        """Bellman Optimality Temporal Difference Update."""
        current_q = self.q_table[state, action]
        if done:
            target = reward
        else:
            best_next_q = np.max(self.q_table[next_state, :])
            target = reward + self.gamma * best_next_q
            
        td_error = target - current_q
        self.q_table[state, action] += self.lr * td_error
        return float(td_error)

    def decay_exploration(self):
        """Geometric decay of exploration probability."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_policy(self, filepath: str):
        np.save(filepath, self.q_table)

    def load_policy(self, filepath: str):
        self.q_table = np.load(filepath)
