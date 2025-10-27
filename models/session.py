from extensions import db

class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    recurring = db.Column(db.Boolean, default=False)
    weekday = db.Column(db.Integer)  # 0 = Monday, 6 = Sunday
