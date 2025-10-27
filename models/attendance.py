from extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    effort = db.Column(db.Integer)
    discipline = db.Column(db.Integer)

    athlete = db.relationship('Athlete', backref='attendances')
    session = db.relationship('Session', backref='attendances')
