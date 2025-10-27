from extensions import db
from datetime import datetime

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
