"""
Reinforcement Learning Agent for Personalized Learning Paths
Uses Stable-Baselines3 for training and evaluation
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student_profile import StudentProfile, StudentFactory
from models.learning_path import LearningPath, LearningPathBuilder


class PLPAgent:
    """
    Agent for selecting optimal learning paths using Q-learning.
    Simplified implementation that doesn't require stable-baselines3 for basic usage.
    """

    def __init__(self, learning_path: LearningPath, learning_rate: float = 0.1,
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        self.learning_path = learning_path
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Q-table: state -> node_id -> Q-value
        self.q_table: Dict[str, Dict[str, float]] = {}

        # Statistics
        self.training_history: List[Dict] = []

    def _state_key(self, student: StudentProfile, completed: set) -> str:
        """Create a hashable state key"""
        # Discretize student profile for Q-table
        profile_key = f"{int(student.emotional.intrinsic_motivation/20)}_{int(student.cognitive.conceptual_mastery/20)}"
        completed_key = "_".join(sorted(completed))
        return f"{profile_key}|{completed_key}"

    def get_q_values(self, state_key: str) -> Dict[str, float]:
        """Get Q-values for a state, initializing if needed"""
        if state_key not in self.q_table:
            self.q_table[state_key] = {
                node_id: 0.0 for node_id in self.learning_path.nodes.keys()
            }
        return self.q_table[state_key]

    def select_action(self, student: StudentProfile, completed: set,
                      explore: bool = True) -> Optional[str]:
        """Select next node using epsilon-greedy policy"""
        # Get valid actions
        valid_nodes = []
        for node_id, node in self.learning_path.nodes.items():
            if node_id not in completed:
                if all(prereq in completed for prereq in node.prerequisites):
                    valid_nodes.append(node_id)

        if not valid_nodes:
            return None

        state_key = self._state_key(student, completed)
        q_values = self.get_q_values(state_key)

        # Epsilon-greedy selection
        if explore and np.random.random() < self.epsilon:
            return np.random.choice(valid_nodes)
        else:
            # Select best valid action
            best_q = float('-inf')
            best_node = valid_nodes[0]
            for node_id in valid_nodes:
                if q_values[node_id] > best_q:
                    best_q = q_values[node_id]
                    best_node = node_id
            return best_node

    def update_q_value(self, state_key: str, action: str, reward: float,
                       next_state_key: str, done: bool):
        """Update Q-value using Q-learning update rule"""
        q_values = self.get_q_values(state_key)
        next_q_values = self.get_q_values(next_state_key)

        if done:
            target = reward
        else:
            target = reward + self.discount_factor * max(next_q_values.values())

        q_values[action] = q_values[action] + self.learning_rate * (target - q_values[action])

    def get_optimal_path(self, student: StudentProfile) -> List[str]:
        """Get the optimal path for a student using learned Q-values"""
        path = []
        completed = set()
        max_steps = len(self.learning_path.nodes) * 2

        for _ in range(max_steps):
            action = self.select_action(student, completed, explore=False)
            if action is None:
                break
            path.append(action)
            completed.add(action)

            # Check if final reached
            if action == 'final':
                break

        return path


def simulate_learning(student: StudentProfile, node_id: str,
                      learning_path: LearningPath) -> Tuple[float, Dict]:
    """Simulate a student completing a learning node"""
    node = learning_path.nodes.get(node_id)
    if not node:
        return -1.0, {'error': 'Node not found'}

    # Calculate base performance
    skill_match = student.cognitive.prior_knowledge.get(node.skill.value, 50.0) / 100.0
    difficulty_factor = 1.0 - (node.difficulty.value - 1) * 0.15
    motivation_factor = student.emotional.intrinsic_motivation / 100.0
    efficacy_factor = student.emotional.self_efficacy / 100.0

    base_score = (0.3 * skill_match + 0.25 * motivation_factor +
                  0.25 * efficacy_factor + 0.2 * difficulty_factor)

    noise = np.random.normal(0, 0.08)
    score = np.clip(base_score + noise, 0.0, 1.0)

    # Update student knowledge
    skill_key = node.skill.value
    current = student.cognitive.prior_knowledge.get(skill_key, 50.0)
    gain = score * 8 * (1 - current / 100.0)
    student.cognitive.prior_knowledge[skill_key] = min(100.0, current + gain)

    # Update motivation
    if score > 0.7:
        student.emotional.intrinsic_motivation = min(100.0,
            student.emotional.intrinsic_motivation + 1.5)

    metrics = {
        'score': score * 100,
        'knowledge_gain': gain,
        'time_spent': node.estimated_duration * (1 + (1 - score) * 0.3)
    }

    return score, metrics


def train_agent(learning_path: LearningPath, base_student: StudentProfile,
                num_episodes: int = 500, num_clones: int = 50) -> PLPAgent:
    """
    Train the RL agent using virtual student clones.

    Args:
        learning_path: The learning path structure
        base_student: Base student profile to clone
        num_episodes: Number of training episodes
        num_clones: Number of virtual clones to create

    Returns:
        Trained PLPAgent
    """
    agent = PLPAgent(learning_path)

    # Create virtual clones
    clones = [StudentFactory.create_virtual_clone(base_student, variation=0.15)
              for _ in range(num_clones)]

    training_stats = []

    for episode in range(num_episodes):
        # Select a random clone
        student = StudentFactory.create_virtual_clone(
            clones[episode % num_clones], variation=0.05
        )

        completed = set()
        episode_reward = 0.0
        episode_length = 0

        for step in range(len(learning_path.nodes) * 2):
            state_key = agent._state_key(student, completed)

            # Select action
            action = agent.select_action(student, completed, explore=True)
            if action is None:
                break

            # Simulate learning
            reward, metrics = simulate_learning(student, action, learning_path)

            if metrics.get('score', 0) >= 50:
                completed.add(action)

            # Next state
            next_state_key = agent._state_key(student, completed)

            # Check if done
            done = (action == 'final' and action in completed) or len(completed) >= len(learning_path.nodes) - 1

            # Bonus for completion
            if done and 'final' in completed:
                reward += 0.5

            # Update Q-value
            agent.update_q_value(state_key, action, reward, next_state_key, done)

            episode_reward += reward
            episode_length += 1

            if done:
                break

        # Decay epsilon
        agent.epsilon = max(0.01, agent.epsilon * 0.995)

        if episode % 50 == 0:
            training_stats.append({
                'episode': episode,
                'reward': episode_reward,
                'length': episode_length,
                'epsilon': agent.epsilon
            })

    agent.training_history = training_stats
    return agent


def simulate_scenarios(agent: PLPAgent, base_student: StudentProfile,
                       num_simulations: int = 100) -> Dict:
    """
    Run simulations to find optimal paths and gather statistics.

    Args:
        agent: Trained PLPAgent
        base_student: Base student profile
        num_simulations: Number of simulation runs

    Returns:
        Dictionary with simulation results
    """
    results = {
        'paths': [],
        'rewards': [],
        'completion_rates': [],
        'knowledge_gains': {}
    }

    for skill in ['literacy', 'numeracy', 'digital', 'citizenship']:
        results['knowledge_gains'][skill] = []

    for _ in range(num_simulations):
        student = StudentFactory.create_virtual_clone(base_student, variation=0.1)
        initial_knowledge = dict(student.cognitive.prior_knowledge)

        path = []
        completed = set()
        total_reward = 0.0

        for _ in range(len(agent.learning_path.nodes) * 2):
            action = agent.select_action(student, completed, explore=False)
            if action is None:
                break

            reward, metrics = simulate_learning(student, action, agent.learning_path)
            if metrics.get('score', 0) >= 50:
                completed.add(action)
                path.append(action)

            total_reward += reward

            if action == 'final' and action in completed:
                break

        results['paths'].append(path)
        results['rewards'].append(total_reward)
        results['completion_rates'].append(len(completed) / len(agent.learning_path.nodes))

        for skill in ['literacy', 'numeracy', 'digital', 'citizenship']:
            gain = student.cognitive.prior_knowledge.get(skill, 0) - initial_knowledge.get(skill, 0)
            results['knowledge_gains'][skill].append(gain)

    # Calculate statistics
    results['average_reward'] = np.mean(results['rewards'])
    results['std_reward'] = np.std(results['rewards'])
    results['average_completion'] = np.mean(results['completion_rates'])

    # Find most common optimal path
    path_counts = {}
    for path in results['paths']:
        path_key = '->'.join(path)
        path_counts[path_key] = path_counts.get(path_key, 0) + 1

    if path_counts:
        optimal_path_key = max(path_counts, key=path_counts.get)
        results['optimal_path'] = optimal_path_key.split('->')
        results['optimal_path_frequency'] = path_counts[optimal_path_key] / num_simulations
    else:
        results['optimal_path'] = []
        results['optimal_path_frequency'] = 0

    results['average_knowledge_gains'] = {
        skill: np.mean(gains) for skill, gains in results['knowledge_gains'].items()
    }

    return results
