from datetime import datetime
from extensions import db

class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    belt = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    effort = db.Column(db.Integer, default=0)
    discipline = db.Column(db.Integer, default=0)

    athlete = db.relationship('Athlete', backref='attendances')
    session = db.relationship('Session', backref='attendances')
