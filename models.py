print("✅ models.py loaded — weight is active")
print("✅ Loaded models.py")

from extensions import db
from flask_login import UserMixin
from datetime import datetime

# 🔐 Login User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

# 🧍 Athlete Model
class Athlete(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    belt = db.Column(db.String, nullable=True)
    weight = db.Column(db.Float, nullable=True)            # ✅ Optional
    gender = db.Column(db.String, nullable=True)           # ✅ Optional
    date_of_birth = db.Column(db.Date, nullable=True)      # ✅ Optional
    created_at = db.Column(db.DateTime, default=db.func.now())

    attendances = db.relationship('Attendance', backref='athlete', lazy='dynamic')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def attendance_summary(self):
        total_sessions = self.attendances.count()
        if total_sessions == 0:
            return {"total": 0, "avg_effort": 0, "avg_discipline": 0}
        avg_effort = db.session.query(db.func.avg(Attendance.effort)).filter_by(athlete_id=self.id).scalar()
        avg_discipline = db.session.query(db.func.avg(Attendance.discipline)).filter_by(athlete_id=self.id).scalar()
        return {
            "total": total_sessions,
            "avg_effort": round(avg_effort or 0, 1),
            "avg_discipline": round(avg_discipline or 0, 1)
        }

    def __repr__(self):
        return f"<Athlete {self.full_name()} - {self.belt}>"

# 📅 Session Model
class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)               # e.g. "BJJ Fundamentals"
    type = db.Column(db.String(50), nullable=True)                 # e.g. "BJJ", "Wrestling"
    date = db.Column(db.DateTime, nullable=False)                  # Full datetime (from start_date + start_time)
    location = db.Column(db.String(100), nullable=True)            # Optional location
    coach_name = db.Column(db.String(100), nullable=True)          # Optional coach name
    created_at = db.Column(db.DateTime, default=db.func.now())

    attendances = db.relationship('Attendance', backref='session', lazy='dynamic')

    def __repr__(self):
        return f"<Session {self.name} on {self.date.strftime('%Y-%m-%d %H:%M')}>"
