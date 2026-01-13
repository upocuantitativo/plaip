"""
Database models using SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class StudentModel(db.Model):
    """Database model for students"""
    __tablename__ = 'students'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profile_data = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress_records = db.relationship('ProgressRecord', backref='student', lazy=True)


class LearningPathModel(db.Model):
    """Database model for learning paths"""
    __tablename__ = 'learning_paths'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    path_data = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProgressRecord(db.Model):
    """Database model for student progress"""
    __tablename__ = 'progress_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    node_id = db.Column(db.String(50), nullable=False)
    path_id = db.Column(db.String(50), db.ForeignKey('learning_paths.id'), nullable=False)

    # Performance metrics
    score = db.Column(db.Float, default=0.0)
    time_spent_minutes = db.Column(db.Float, default=0.0)
    attempts = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)

    # Feedback data
    feedback_data = db.Column(db.Text)  # JSON

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SimulationResult(db.Model):
    """Database model for RL simulation results"""
    __tablename__ = 'simulation_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), nullable=False)
    path_id = db.Column(db.String(50), nullable=False)

    # Simulation parameters
    num_clones = db.Column(db.Integer, default=100)
    episodes = db.Column(db.Integer, default=1000)

    # Results
    optimal_path = db.Column(db.Text)  # JSON list of node IDs
    average_reward = db.Column(db.Float)
    success_rate = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db(app):
    """Initialize the database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
