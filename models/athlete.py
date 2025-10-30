from extensions import db
from datetime import datetime

class Athlete(db.Model):
    __tablename__ = 'athlete'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    belt = db.Column(db.String(30), nullable=False)
    weight = db.Column(db.Float, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    group = db.Column(db.String(50), nullable=True)  # ✅ Discipline group (e.g. Kids BJJ, LOGA MMA)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def attendance_summary(self):
        # Placeholder logic — update this when attendance tracking is wired up
        return {
            "total": 0,
            "avg_effort": "—",
            "avg_discipline": "—"
        }

    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
