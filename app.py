"""
PLAIP - Personalized Learning's Artificial Intelligence Paths
Flask Web Application

Main application for managing and visualizing personalized learning paths
with reinforcement learning optimization.
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import json
from datetime import datetime

# Import models
from models.student_profile import StudentProfile, StudentFactory, DemographicVariables, EmotionalFactors, CognitiveFactors, EducationStage, Gender, KolbStyle
from models.learning_path import LearningPath, LearningPathBuilder, BasicSkill
from models.database import db, init_db, StudentModel, LearningPathModel, ProgressRecord, SimulationResult

# Import RL components
from rl.agent import PLPAgent, train_agent, simulate_scenarios

# Import visualization
from visualization.tree import generate_tree_data, generate_performance_chart, generate_optimal_path_visualization

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'plaip-dev-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///plaip.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Global state (in production, use database)
current_learning_path = None
trained_agent = None
students = {}


def get_or_create_learning_path():
    """Get the current learning path or create a default one"""
    global current_learning_path
    if current_learning_path is None:
        current_learning_path = LearningPathBuilder.create_basic_skills_path()
    return current_learning_path


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    path = get_or_create_learning_path()
    return render_template('index.html',
                           path_name=path.name,
                           num_nodes=len(path.nodes),
                           num_students=len(students))


@app.route('/itinerary')
def itinerary():
    """Learning path tree visualization"""
    path = get_or_create_learning_path()
    tree_data = generate_tree_data(path)
    return render_template('itinerary.html',
                           path=path,
                           tree_data=json.dumps(tree_data))


@app.route('/students')
def students_page():
    """Student management page"""
    return render_template('students.html', students=list(students.values()))


@app.route('/simulation')
def simulation():
    """RL Simulation page"""
    return render_template('simulation.html',
                           has_agent=trained_agent is not None,
                           num_students=len(students))


@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    path = get_or_create_learning_path()
    chart_data = generate_performance_chart(path, list(students.values()))
    return render_template('analytics.html', chart_data=json.dumps(chart_data))


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/tree')
def api_tree():
    """Get tree data for visualization"""
    path = get_or_create_learning_path()
    student_id = request.args.get('student_id')
    tree_data = generate_tree_data(path, student_id)
    return jsonify(tree_data)


@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    """Manage students"""
    if request.method == 'GET':
        return jsonify([s.to_dict() for s in students.values()])

    elif request.method == 'POST':
        data = request.json

        # Create student profile
        demographics = DemographicVariables(
            age=data.get('age', 16),
            education_stage=EducationStage[data.get('education_stage', 'ESO')],
            gender=Gender[data.get('gender', 'OTHER')],
            digital_competence_score=data.get('digital_competence', 50.0)
        )

        emotional = EmotionalFactors(
            intrinsic_motivation=data.get('motivation', 50.0),
            self_efficacy=data.get('self_efficacy', 50.0)
        )

        cognitive = CognitiveFactors(
            learning_preferences=data.get('learning_preferences', {}),
            kolb_style=KolbStyle[data.get('kolb_style', 'CONVERGENT')],
            prior_knowledge=data.get('prior_knowledge', {
                'literacy': 50.0, 'numeracy': 50.0,
                'digital': 50.0, 'citizenship': 50.0
            }),
            conceptual_mastery=data.get('conceptual_mastery', 50.0),
            reasoning_logic=data.get('reasoning_logic', 50.0),
            metacognitive_accuracy=data.get('metacognitive_accuracy', 0.25)
        )

        import uuid
        student = StudentProfile(
            id=uuid.uuid4().hex[:12],
            name=data.get('name', 'New Student'),
            demographics=demographics,
            emotional=emotional,
            cognitive=cognitive
        )

        students[student.id] = student
        return jsonify(student.to_dict()), 201


@app.route('/api/students/<student_id>')
def api_student(student_id):
    """Get a specific student"""
    student = students.get(student_id)
    if student:
        return jsonify(student.to_dict())
    return jsonify({'error': 'Student not found'}), 404


@app.route('/api/students/sample', methods=['POST'])
def api_create_sample_students():
    """Create sample students for testing"""
    profiles = ['high_performer', 'average', 'struggling']
    created = []

    for profile_type in profiles:
        student = StudentFactory.create_sample_profile(profile_type)
        students[student.id] = student
        created.append(student.to_dict())

    return jsonify(created), 201


@app.route('/api/simulation/train', methods=['POST'])
def api_train():
    """Train the RL agent"""
    global trained_agent

    data = request.json or {}
    num_episodes = data.get('episodes', 500)
    num_clones = data.get('clones', 50)

    # Get or create a base student
    if students:
        base_student = list(students.values())[0]
    else:
        base_student = StudentFactory.create_sample_profile('average')
        students[base_student.id] = base_student

    path = get_or_create_learning_path()

    # Train agent
    trained_agent = train_agent(path, base_student, num_episodes, num_clones)

    return jsonify({
        'status': 'trained',
        'episodes': num_episodes,
        'clones': num_clones,
        'training_history': trained_agent.training_history
    })


@app.route('/api/simulation/run', methods=['POST'])
def api_run_simulation():
    """Run simulation with trained agent"""
    global trained_agent

    if trained_agent is None:
        return jsonify({'error': 'Agent not trained'}), 400

    data = request.json or {}
    student_id = data.get('student_id')
    num_simulations = data.get('simulations', 100)

    # Get student
    if student_id and student_id in students:
        base_student = students[student_id]
    elif students:
        base_student = list(students.values())[0]
    else:
        base_student = StudentFactory.create_sample_profile('average')

    # Run simulations
    results = simulate_scenarios(trained_agent, base_student, num_simulations)

    # Generate visualization data for optimal path
    path = get_or_create_learning_path()
    optimal_path_viz = generate_optimal_path_visualization(results['optimal_path'], path)

    return jsonify({
        'optimal_path': results['optimal_path'],
        'optimal_path_visualization': optimal_path_viz,
        'average_reward': results['average_reward'],
        'std_reward': results['std_reward'],
        'average_completion': results['average_completion'],
        'optimal_path_frequency': results['optimal_path_frequency'],
        'average_knowledge_gains': results['average_knowledge_gains']
    })


@app.route('/api/simulation/optimal-path/<student_id>')
def api_optimal_path(student_id):
    """Get optimal path for a specific student"""
    global trained_agent

    if trained_agent is None:
        return jsonify({'error': 'Agent not trained'}), 400

    student = students.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    optimal_path = trained_agent.get_optimal_path(student)
    path = get_or_create_learning_path()
    viz_data = generate_optimal_path_visualization(optimal_path, path)

    return jsonify({
        'student_id': student_id,
        'optimal_path': optimal_path,
        'visualization': viz_data
    })


@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Record feedback and adjust learning path"""
    data = request.json
    student_id = data.get('student_id')
    node_id = data.get('node_id')
    score = data.get('score', 0)
    feedback_text = data.get('feedback', '')

    path = get_or_create_learning_path()
    node = path.nodes.get(node_id)

    if node and student_id in students:
        student = students[student_id]

        # Update node performance
        from models.learning_path import PerformanceIndicators
        if student_id not in node.student_performance:
            node.student_performance[student_id] = PerformanceIndicators()

        perf = node.student_performance[student_id]
        perf.attempts += 1
        perf.average_score = (perf.average_score * (perf.attempts - 1) + score) / perf.attempts

        if score >= 50:
            perf.completion_rate = 100.0
            if node_id not in student.completed_nodes:
                student.completed_nodes.append(node_id)

        # Update student profile based on feedback
        student.performance_history.append({
            'node_id': node_id,
            'score': score,
            'feedback': feedback_text,
            'timestamp': datetime.now().isoformat()
        })

        return jsonify({'status': 'recorded', 'updated_performance': perf.to_dict()})

    return jsonify({'error': 'Student or node not found'}), 404


@app.route('/api/path/redesign', methods=['POST'])
def api_redesign_path():
    """Redesign learning path based on feedback"""
    global current_learning_path, trained_agent

    data = request.json or {}

    # Collect performance data from all students
    performance_summary = {}
    path = get_or_create_learning_path()

    for node_id, node in path.nodes.items():
        scores = []
        for student_id, perf in node.student_performance.items():
            if perf.average_score > 0:
                scores.append(perf.average_score)

        if scores:
            performance_summary[node_id] = {
                'average_score': sum(scores) / len(scores),
                'num_attempts': len(scores),
                'needs_improvement': sum(scores) / len(scores) < 60
            }

    # Identify nodes that need adjustment
    nodes_to_adjust = [
        node_id for node_id, summary in performance_summary.items()
        if summary.get('needs_improvement', False)
    ]

    # Retrain agent if there are adjustments
    if nodes_to_adjust and students:
        base_student = list(students.values())[0]
        trained_agent = train_agent(path, base_student, num_episodes=300, num_clones=30)

    return jsonify({
        'performance_summary': performance_summary,
        'nodes_adjusted': nodes_to_adjust,
        'agent_retrained': len(nodes_to_adjust) > 0
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Create sample data on startup
    with app.app_context():
        # Create sample students if none exist
        if not students:
            for profile_type in ['high_performer', 'average', 'struggling']:
                student = StudentFactory.create_sample_profile(profile_type)
                students[student.id] = student

    app.run(debug=True, host='0.0.0.0', port=5000)
