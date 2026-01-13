"""
Visualization utilities for learning path trees
Generates data structures for D3.js visualization
"""
from typing import Dict, List, Optional
import json


def generate_tree_data(learning_path, student_id: Optional[str] = None) -> Dict:
    """
    Generate hierarchical tree data for D3.js visualization.

    Args:
        learning_path: LearningPath object
        student_id: Optional student ID to include student-specific performance

    Returns:
        Dictionary structure compatible with D3.js hierarchy
    """
    # Color mapping for skills
    skill_colors = {
        'literacy': '#4CAF50',      # Green
        'numeracy': '#2196F3',      # Blue
        'digital': '#9C27B0',       # Purple
        'citizenship': '#FF9800'    # Orange
    }

    def build_node_data(node) -> Dict:
        """Build data for a single node"""
        # Get performance data
        if student_id and student_id in node.student_performance:
            perf = node.student_performance[student_id]
        else:
            perf = node.performance

        return {
            'id': node.id,
            'name': node.title,
            'skill': node.skill.value,
            'skillColor': skill_colors.get(node.skill.value, '#666666'),
            'difficulty': node.difficulty.value,
            'difficultyLabel': ['', 'Basico', 'Elemental', 'Intermedio', 'Avanzado'][node.difficulty.value],
            'description': node.description,
            'estimatedDuration': node.estimated_duration,
            'objectives': node.learning_objectives,
            'strategies': [s.value for s in node.recommended_strategies],
            'methodology': node.methodology.value,
            'performance': {
                'completionRate': round(perf.completion_rate, 1),
                'averageScore': round(perf.average_score, 1),
                'timeSpent': round(perf.time_spent_minutes, 1),
                'attempts': perf.attempts,
                'retentionRate': round(perf.retention_rate, 1)
            },
            'prerequisites': node.prerequisites,
            'nextNodes': node.next_nodes
        }

    def build_subtree(node_id: str, visited: set, depth: int = 0) -> Optional[Dict]:
        """Recursively build tree structure"""
        if node_id in visited or depth > 10:
            return None

        visited.add(node_id)
        node = learning_path.nodes.get(node_id)
        if not node:
            return None

        node_data = build_node_data(node)
        node_data['depth'] = depth

        children = []
        for next_id in node.next_nodes:
            child = build_subtree(next_id, visited.copy(), depth + 1)
            if child:
                children.append(child)

        if children:
            node_data['children'] = children

        return node_data

    # Build from root nodes
    roots = []
    for root_id in learning_path.root_nodes:
        tree = build_subtree(root_id, set())
        if tree:
            roots.append(tree)

    return {
        'name': learning_path.name,
        'description': learning_path.description,
        'targetSkills': [s.value for s in learning_path.target_skills],
        'children': roots,
        'skillColors': skill_colors
    }


def generate_performance_chart(learning_path, students: List) -> Dict:
    """
    Generate data for performance charts.

    Args:
        learning_path: LearningPath object
        students: List of StudentProfile objects

    Returns:
        Chart data structure
    """
    # Aggregate performance by skill
    skill_performance = {
        'literacy': {'scores': [], 'times': [], 'completion': []},
        'numeracy': {'scores': [], 'times': [], 'completion': []},
        'digital': {'scores': [], 'times': [], 'completion': []},
        'citizenship': {'scores': [], 'times': [], 'completion': []}
    }

    for node_id, node in learning_path.nodes.items():
        skill = node.skill.value
        if skill in skill_performance:
            if node.performance.average_score > 0:
                skill_performance[skill]['scores'].append(node.performance.average_score)
            if node.performance.time_spent_minutes > 0:
                skill_performance[skill]['times'].append(node.performance.time_spent_minutes)
            if node.performance.completion_rate > 0:
                skill_performance[skill]['completion'].append(node.performance.completion_rate)

    # Calculate averages
    chart_data = {
        'skills': [],
        'averageScores': [],
        'averageTimes': [],
        'completionRates': []
    }

    for skill, data in skill_performance.items():
        chart_data['skills'].append(skill.capitalize())
        chart_data['averageScores'].append(
            sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        )
        chart_data['averageTimes'].append(
            sum(data['times']) / len(data['times']) if data['times'] else 0
        )
        chart_data['completionRates'].append(
            sum(data['completion']) / len(data['completion']) if data['completion'] else 0
        )

    # Student progress data
    student_progress = []
    for student in students:
        progress = {
            'id': student.id,
            'name': student.name,
            'completedNodes': len(student.completed_nodes),
            'totalNodes': len(learning_path.nodes),
            'currentKnowledge': student.cognitive.prior_knowledge,
            'motivation': student.emotional.intrinsic_motivation,
            'selfEfficacy': student.emotional.self_efficacy
        }
        student_progress.append(progress)

    chart_data['studentProgress'] = student_progress

    return chart_data


def generate_optimal_path_visualization(optimal_path: List[str], learning_path) -> Dict:
    """
    Generate visualization data for the optimal learning path.

    Args:
        optimal_path: List of node IDs in optimal order
        learning_path: LearningPath object

    Returns:
        Visualization data
    """
    path_data = {
        'nodes': [],
        'edges': [],
        'totalDuration': 0
    }

    for i, node_id in enumerate(optimal_path):
        node = learning_path.nodes.get(node_id)
        if node:
            path_data['nodes'].append({
                'id': node_id,
                'order': i + 1,
                'name': node.title,
                'skill': node.skill.value,
                'difficulty': node.difficulty.value,
                'duration': node.estimated_duration
            })
            path_data['totalDuration'] += node.estimated_duration

            if i > 0:
                path_data['edges'].append({
                    'source': optimal_path[i - 1],
                    'target': node_id
                })

    return path_data
