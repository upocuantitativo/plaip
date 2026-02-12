"""
InfiniteLearner - AI-powered Personalised Learning Pathways for Basic Skills
Flask Web Application

European Policy Experimentation (Erasmus+ KA3)
ERASMUS-EDU-2026-POL-EXP-T03-DIGITAL-BS

Main application for managing and visualizing personalized learning paths
with reinforcement learning optimization.
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, g
import os
import json
from datetime import datetime

SUPPORTED_LANGS = ('en', 'es', 'de')

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
    """Redirect to default language landing page"""
    return redirect(url_for('landing', lang='en'))


@app.route('/<lang>/itinerary')
def itinerary(lang='en'):
    """Learning path tree visualization"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('itinerary', lang='en'))
    path = get_or_create_learning_path()
    tree_data = generate_tree_data(path)
    return render_template(f'{lang}/itinerary.html',
                           path=path,
                           tree_data=json.dumps(tree_data),
                           lang=lang)


@app.route('/<lang>/students')
def students_page(lang='en'):
    """Student management page"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('students_page', lang='en'))
    return render_template(f'{lang}/students.html', students=list(students.values()), lang=lang)


@app.route('/<lang>/simulation')
def simulation(lang='en'):
    """RL Simulation page"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('simulation', lang='en'))
    return render_template(f'{lang}/simulation.html',
                           has_agent=trained_agent is not None,
                           num_students=len(students),
                           lang=lang)


@app.route('/<lang>/analytics')
def analytics(lang='en'):
    """Analytics dashboard"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('analytics', lang='en'))
    path = get_or_create_learning_path()
    chart_data = generate_performance_chart(path, list(students.values()))
    return render_template(f'{lang}/analytics.html', chart_data=json.dumps(chart_data), lang=lang)


# ============================================================================
# New Routes - InfiniteLearner Structure
# ============================================================================

@app.route('/<lang>/landing')
def landing(lang='en'):
    """Project landing page for partner recruitment"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('landing', lang='en'))
    return render_template(f'{lang}/landing.html', lang=lang)


@app.route('/<lang>/framework')
def framework(lang='en'):
    """WP2 - Shared Pedagogical Framework"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('framework', lang='en'))
    path = get_or_create_learning_path()
    return render_template(f'{lang}/framework.html', path=path, lang=lang)


@app.route('/<lang>/toolkit')
def toolkit(lang='en'):
    """WP2 - Toolkit for Teachers"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('toolkit', lang='en'))
    return render_template(f'{lang}/toolkit.html', lang=lang)


@app.route('/<lang>/diagnostic')
def diagnostic(lang='en'):
    """WP3 - Initial Diagnostic Assessment"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('diagnostic', lang='en'))
    return render_template(f'{lang}/diagnostic.html', students=list(students.values()), lang=lang)


@app.route('/<lang>/activities')
def activities(lang='en'):
    """WP3 - Learning Activities"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('activities', lang='en'))
    path = get_or_create_learning_path()
    return render_template(f'{lang}/activities.html', path=path, students=list(students.values()), lang=lang)


@app.route('/<lang>/evaluation')
def evaluation(lang='en'):
    """WP3 - Formative Evaluation"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('evaluation', lang='en'))
    path = get_or_create_learning_path()
    return render_template(f'{lang}/evaluation.html', path=path, students=list(students.values()), lang=lang)


@app.route('/<lang>/dashboard/teacher')
def dashboard_teacher(lang='en'):
    """Teacher Dashboard - Observable Learning Signals"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('dashboard_teacher', lang='en'))
    path = get_or_create_learning_path()
    return render_template(f'{lang}/dashboard_teacher.html',
                          path=path,
                          students=list(students.values()),
                          num_students=len(students),
                          lang=lang)


@app.route('/<lang>/dashboard/student')
def dashboard_student(lang='en'):
    """Student Dashboard - Personal Progress"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('dashboard_student', lang='en'))
    return render_template(f'{lang}/dashboard_student.html', students=list(students.values()), lang=lang)


@app.route('/<lang>/recommendations')
def recommendations(lang='en'):
    """AI Recommendations - Next Steps Suggestions"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('recommendations', lang='en'))
    path = get_or_create_learning_path()
    return render_template(f'{lang}/recommendations.html',
                          path=path,
                          students=list(students.values()),
                          has_agent=trained_agent is not None,
                          lang=lang)


@app.route('/<lang>/consolidation')
def consolidation(lang='en'):
    """WP4 - Results Consolidation and Recommendations"""
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('consolidation', lang='en'))
    path = get_or_create_learning_path()
    chart_data = generate_performance_chart(path, list(students.values()))
    return render_template(f'{lang}/consolidation.html',
                          path=path,
                          students=list(students.values()),
                          chart_data=json.dumps(chart_data),
                          lang=lang)


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/tree')
def api_tree():
    """Get tree data for visualization with filters"""
    path = get_or_create_learning_path()
    student_id = request.args.get('student_id')

    # Get filter parameters
    profile_type = request.args.get('profile', 'all')
    gender = request.args.get('gender', 'all')
    age_range = request.args.get('age', 'all')
    skill_filter = request.args.get('skill', 'all')

    # Generate personalized tree based on filters
    tree_data = generate_personalized_tree(path, profile_type, gender, age_range, skill_filter)
    return jsonify(tree_data)


def generate_personalized_tree(path, profile_type, gender, age_range, skill_filter):
    """Generate a personalized tree based on profile filters"""
    from visualization.tree import generate_tree_data
    import random

    # Base tree data
    tree_data = generate_tree_data(path)

    # Profile-based difficulty adjustments
    difficulty_adjustments = {
        'high_performer': {'base_score': 75, 'completion': 85, 'retention': 80},
        'average': {'base_score': 55, 'completion': 60, 'retention': 55},
        'struggling': {'base_score': 35, 'completion': 40, 'retention': 30},
        'all': {'base_score': 55, 'completion': 60, 'retention': 55}
    }

    # Age-based adjustments
    age_adjustments = {
        '12-14': {'score_mod': -10, 'time_mod': 1.3},
        '15-16': {'score_mod': 0, 'time_mod': 1.0},
        '17-18': {'score_mod': 5, 'time_mod': 0.9},
        '19+': {'score_mod': 10, 'time_mod': 0.8},
        'all': {'score_mod': 0, 'time_mod': 1.0}
    }

    # Gender-based engagement patterns (research-based differences)
    gender_patterns = {
        'female': {'literacy_boost': 5, 'citizenship_boost': 3, 'digital_boost': 0},
        'male': {'literacy_boost': -2, 'citizenship_boost': 0, 'digital_boost': 5},
        'non_binary': {'literacy_boost': 2, 'citizenship_boost': 5, 'digital_boost': 2},
        'all': {'literacy_boost': 0, 'citizenship_boost': 0, 'digital_boost': 0}
    }

    profile_adj = difficulty_adjustments.get(profile_type, difficulty_adjustments['all'])
    age_adj = age_adjustments.get(age_range, age_adjustments['all'])
    gender_adj = gender_patterns.get(gender, gender_patterns['all'])

    def adjust_node(node):
        """Recursively adjust node performance based on filters"""
        if 'performance' in node:
            skill = node.get('skill', '')

            # Base score from profile
            base = profile_adj['base_score']

            # Age adjustment
            base += age_adj['score_mod']

            # Gender-skill adjustment
            if skill == 'literacy':
                base += gender_adj['literacy_boost']
            elif skill == 'citizenship':
                base += gender_adj['citizenship_boost']
            elif skill == 'digital':
                base += gender_adj['digital_boost']

            # Add randomness
            base += random.randint(-8, 8)
            base = max(10, min(95, base))

            node['performance']['averageScore'] = round(base, 1)
            node['performance']['completionRate'] = round(
                profile_adj['completion'] + age_adj['score_mod'] / 2 + random.randint(-5, 5), 1
            )
            node['performance']['retentionRate'] = round(
                profile_adj['retention'] + random.randint(-10, 10), 1
            )
            node['performance']['timeSpent'] = round(
                (node.get('estimatedDuration', 30) or 30) * age_adj['time_mod'] * random.uniform(0.8, 1.2), 1
            )
            node['performance']['attempts'] = random.randint(1, 3) if profile_type == 'high_performer' else random.randint(2, 5)

        # Adjust visibility based on skill filter
        if skill_filter != 'all' and node.get('skill') != skill_filter:
            node['filtered'] = True
        else:
            node['filtered'] = False

        # Process children
        if 'children' in node and node['children']:
            for child in node['children']:
                adjust_node(child)

    # Adjust root and all children
    if 'children' in tree_data:
        for child in tree_data['children']:
            adjust_node(child)

    # Add filter metadata
    tree_data['appliedFilters'] = {
        'profile': profile_type,
        'gender': gender,
        'ageRange': age_range,
        'skill': skill_filter
    }

    return tree_data


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
    lang = request.path.split('/')[1] if len(request.path.split('/')) > 1 else 'en'
    if lang not in SUPPORTED_LANGS:
        lang = 'en'
    return render_template(f'{lang}/404.html', lang=lang), 404


@app.errorhandler(500)
def server_error(e):
    lang = request.path.split('/')[1] if len(request.path.split('/')) > 1 else 'en'
    if lang not in SUPPORTED_LANGS:
        lang = 'en'
    return render_template(f'{lang}/500.html', lang=lang), 500


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
