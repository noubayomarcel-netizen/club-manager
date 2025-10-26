from flask import Flask, render_template, request, redirect
from datetime import datetime

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
