from extensions import db
from datetime import datetime

class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)  # ✅ Add this line
    location = db.Column(db.String(100), nullable=True)
    coach_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Session {self.name} on {self.date.strftime('%Y-%m-%d')}>"
    recurring = db.Column(db.Boolean, default=False)
    recurring = db.Column(db.Boolean, default=False)
    weekday = db.Column(db.String(10), nullable=True)  # e.g. "Monday", "Tuesday"
    time = db.Column(db.Time, nullable=True)           # e.g. 17:00

    date = db.Column(db.DateTime, nullable=True)
