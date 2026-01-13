"""
Reinforcement Learning Environment for Personalized Learning Paths
Gymnasium-compatible environment for training agents to optimize learning paths
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student_profile import StudentProfile, StudentFactory
from models.learning_path import LearningPath, LearningNode, BasicSkill


class LearningEnvironment(gym.Env):
    """
    Gymnasium environment for simulating personalized learning paths.

    The agent learns to select optimal next nodes based on student profile
    and current state to maximize learning outcomes.
    """

    metadata = {'render_modes': ['human', 'rgb_array']}

    def __init__(self, learning_path: LearningPath, student: StudentProfile,
                 max_steps: int = 50, render_mode: Optional[str] = None):
        super().__init__()

        self.learning_path = learning_path
        self.original_student = student
        self.student = student
        self.max_steps = max_steps
        self.render_mode = render_mode

        # State space: student vector + current node one-hot + completed nodes
        self.num_nodes = len(learning_path.nodes)
        self.node_ids = list(learning_path.nodes.keys())

        # Student vector (13 dimensions) + current node (num_nodes) + completed (num_nodes)
        state_dim = 13 + self.num_nodes + self.num_nodes
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(state_dim,), dtype=np.float32
        )

        # Action space: select one of the possible next nodes
        self.action_space = spaces.Discrete(self.num_nodes)

        # Episode state
        self.current_step = 0
        self.current_node_id = None
        self.completed_nodes = set()
        self.episode_rewards = []

    def _get_observation(self) -> np.ndarray:
        """Convert current state to observation vector"""
        # Student profile vector
        student_vec = self.student.to_vector()

        # Current node one-hot
        current_node_vec = np.zeros(self.num_nodes, dtype=np.float32)
        if self.current_node_id:
            idx = self.node_ids.index(self.current_node_id)
            current_node_vec[idx] = 1.0

        # Completed nodes binary vector
        completed_vec = np.zeros(self.num_nodes, dtype=np.float32)
        for node_id in self.completed_nodes:
            if node_id in self.node_ids:
                idx = self.node_ids.index(node_id)
                completed_vec[idx] = 1.0

        return np.concatenate([student_vec, current_node_vec, completed_vec])

    def _simulate_learning_outcome(self, node: LearningNode) -> Tuple[float, Dict]:
        """
        Simulate the learning outcome when a student completes a node.
        Returns reward and updated metrics.
        """
        # Base performance based on student profile matching node requirements
        skill_match = self.student.cognitive.prior_knowledge.get(node.skill.value, 50.0) / 100.0
        difficulty_factor = 1.0 - (node.difficulty.value - 1) * 0.15

        # Emotional factors affect learning
        motivation_factor = self.student.emotional.intrinsic_motivation / 100.0
        efficacy_factor = self.student.emotional.self_efficacy / 100.0

        # Cognitive factors
        reasoning_factor = self.student.cognitive.reasoning_logic / 100.0

        # Calculate base score with some randomness
        base_score = (
            0.3 * skill_match +
            0.2 * motivation_factor +
            0.2 * efficacy_factor +
            0.2 * reasoning_factor +
            0.1 * difficulty_factor
        )

        # Add noise for realism
        noise = np.random.normal(0, 0.1)
        score = np.clip(base_score + noise, 0.0, 1.0)

        # Calculate reward
        reward = score

        # Bonus for completing high-difficulty nodes
        if node.difficulty.value >= 3 and score > 0.7:
            reward += 0.2

        # Penalty for struggling (low score on easy nodes)
        if node.difficulty.value == 1 and score < 0.5:
            reward -= 0.1

        # Update student's knowledge
        skill_key = node.skill.value
        current_knowledge = self.student.cognitive.prior_knowledge.get(skill_key, 50.0)
        knowledge_gain = score * 10 * (1 - current_knowledge / 100.0)  # Diminishing returns
        self.student.cognitive.prior_knowledge[skill_key] = min(100.0, current_knowledge + knowledge_gain)

        # Update motivation based on success
        if score > 0.7:
            self.student.emotional.intrinsic_motivation = min(100.0,
                self.student.emotional.intrinsic_motivation + 2)
            self.student.emotional.self_efficacy = min(100.0,
                self.student.emotional.self_efficacy + 3)
        elif score < 0.4:
            self.student.emotional.intrinsic_motivation = max(0.0,
                self.student.emotional.intrinsic_motivation - 1)

        metrics = {
            'score': score * 100,
            'time_spent': node.estimated_duration * (1 + (1 - score) * 0.5),
            'knowledge_gain': knowledge_gain
        }

        return reward, metrics

    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None
              ) -> Tuple[np.ndarray, Dict]:
        """Reset the environment for a new episode"""
        super().reset(seed=seed)

        # Reset student to clone of original (with variation)
        self.student = StudentFactory.create_virtual_clone(
            self.original_student, variation=0.05
        )

        self.current_step = 0
        self.current_node_id = None
        self.completed_nodes = set()
        self.episode_rewards = []

        return self._get_observation(), {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action: Index of the node to attempt next

        Returns:
            observation, reward, terminated, truncated, info
        """
        self.current_step += 1

        # Get selected node
        if action >= len(self.node_ids):
            # Invalid action
            return self._get_observation(), -1.0, False, False, {'error': 'Invalid action'}

        selected_node_id = self.node_ids[action]
        selected_node = self.learning_path.nodes.get(selected_node_id)

        if not selected_node:
            return self._get_observation(), -1.0, False, False, {'error': 'Node not found'}

        # Check if prerequisites are met
        if not all(prereq in self.completed_nodes for prereq in selected_node.prerequisites):
            # Penalty for trying to skip prerequisites
            return self._get_observation(), -0.5, False, False, {'error': 'Prerequisites not met'}

        # Check if already completed
        if selected_node_id in self.completed_nodes:
            return self._get_observation(), -0.2, False, False, {'error': 'Already completed'}

        # Simulate learning outcome
        reward, metrics = self._simulate_learning_outcome(selected_node)

        # Mark as completed if score is sufficient
        if metrics['score'] >= 50:
            self.completed_nodes.add(selected_node_id)
            self.current_node_id = selected_node_id

        self.episode_rewards.append(reward)

        # Check termination conditions
        terminated = False
        truncated = False

        # Check if final node completed
        if 'final' in self.completed_nodes:
            terminated = True
            reward += 1.0  # Bonus for completing the path

        # Check if all required nodes completed
        required_nodes = set(self.learning_path.root_nodes)
        if required_nodes.issubset(self.completed_nodes):
            reward += 0.5

        # Truncate if max steps reached
        if self.current_step >= self.max_steps:
            truncated = True

        info = {
            'metrics': metrics,
            'completed_nodes': list(self.completed_nodes),
            'current_knowledge': dict(self.student.cognitive.prior_knowledge),
            'motivation': self.student.emotional.intrinsic_motivation
        }

        return self._get_observation(), reward, terminated, truncated, info

    def get_valid_actions(self) -> List[int]:
        """Get list of valid action indices (nodes that can be attempted)"""
        valid = []
        for i, node_id in enumerate(self.node_ids):
            node = self.learning_path.nodes[node_id]
            # Can attempt if prerequisites met and not completed
            if (all(prereq in self.completed_nodes for prereq in node.prerequisites)
                and node_id not in self.completed_nodes):
                valid.append(i)
        return valid

    def render(self):
        """Render the environment state"""
        if self.render_mode == 'human':
            print(f"\nStep {self.current_step}")
            print(f"Current node: {self.current_node_id}")
            print(f"Completed: {self.completed_nodes}")
            print(f"Total reward: {sum(self.episode_rewards):.2f}")
