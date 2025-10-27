from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Athlete(db.Model):
    __tablename__ = 'athlete'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    belt = db.Column(db.String(30))
    style = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    recurring = db.Column(db.Boolean, default=False)
    weekday = db.Column(db.Integer)

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    effort = db.Column(db.Integer)
    discipline = db.Column(db.Integer)

    athlete = db.relationship('Athlete', backref='attendances')
    session = db.relationship('Session', backref='attendances')
