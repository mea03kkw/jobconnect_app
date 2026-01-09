from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='job_seeker')  # 'employer' or 'job_seeker'
    bio = db.Column(db.Text, nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    jobs = db.relationship('Job', backref='user', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    resume_text = db.Column(db.Text, nullable=True)
    resume_file = db.Column(db.String(200), nullable=True)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='applications')
    job = db.relationship('Job', backref='applications')
