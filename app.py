from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import Athlete, Session, Attendance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
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
    name = db.Column(db.String(120), nullable=False)  # e.g., "Gi BJJ - Adults"
    start_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    effort = db.Column(db.Integer, default=0)     # 0-10 scale
    discipline = db.Column(db.Integer, default=0) # 0-10 scale

    athlete = db.relationship('Athlete', backref='attendances')
    session = db.relationship('Session', backref='attendances')

app = Flask(__name__)
attendance_log = []
athlete_profiles = {}
next_id = 1

@app.route('/')
def home():
    return render_template('index.html', log=attendance_log, athlete_profiles=athlete_profiles)

@app.route('/checkin', methods=['POST'])
def checkin():
    name = request.form['name']
    sport = request.form['sport']
    effort = request.form['effort']
    discipline = request.form['discipline']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    attendance_log.append({
        'name': name,
        'sport': sport,
        'effort': effort,
        'discipline': discipline,
        'time': timestamp
    })
    return redirect('/')

@app.route('/add_profile', methods=['POST'])
def add_profile():
    global next_id
    profile = {
        'id': next_id,
        'name': request.form['name'],
        'sport': request.form['sport'],
        'rank': request.form['rank'],
        'weight': request.form['weight'],
        'goal': request.form['goal']
    }
    athlete_profiles[next_id] = profile
    next_id += 1
    return redirect('/')

@app.route('/edit_profile/<int:athlete_id>', methods=['GET'])
def edit_profile(athlete_id):
    athlete = athlete_profiles.get(athlete_id)
    return render_template('edit.html', athlete=athlete)

@app.route('/update_profile/<int:athlete_id>', methods=['POST'])
def update_profile(athlete_id):
    athlete = athlete_profiles.get(athlete_id)
    if athlete:
        athlete['name'] = request.form['name']
        athlete['sport'] = request.form['sport']
        athlete['rank'] = request.form['rank']
        athlete['weight'] = request.form['weight']
        athlete['goal'] = request.form['goal']
    return redirect('/')
