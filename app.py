from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from flask import Flask
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)

# Initialize app and extensions
from flask import Flask
from extensions import db, migrate, login_manager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

from models import User, Athlete, Session, Attendance, Announcement

# Import models
from models import User, Athlete, Session, Attendance, Announcement

# Login manager setup
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------- Routes -------------------

@app.route('/', endpoint='home')
@app.route('/home_summary')
def home_summary():
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (start_of_month + timedelta(days=32)).replace(day=1)

    styles = [
        'Kids BJJ', 'Adults BJJ', 'LOGA MMA', 'CG MMA',
        'Kids Wrestling', 'Adults Wrestling', 'Sheen Wrestling'
    ]

    athlete_counts = {
        style: Athlete.query.filter_by(style=style).count()
        for style in styles
    }

    session_counts = {
        style: Session.query.filter(
            Session.name.contains(style),
            Session.start_time.between(start_of_month, next_month)
        ).count()
        for style in styles
    }

    attendance_counts = {
        style: db.session.query(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.start_time.between(start_of_month, next_month)
        ).count()
        for style in styles
    }

    top_attendees = {}
    for style in styles:
        result = db.session.query(
            Athlete.first_name,
            Athlete.last_name,
            func.count(Attendance.id).label('attendance_count')
        ).join(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.start_time.between(start_of_month, next_month)
        ).group_by(Athlete.id).order_by(func.count(Attendance.id).desc()).first()

        top_attendees[style] = f"{result.first_name} {result.last_name}" if result else '—'

    most_improved = {}
    for style in styles:
        result = db.session.query(
            Athlete.first_name,
            func.avg(Attendance.effort + Attendance.discipline).label('score')
        ).join(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.start_time.between(start_of_month, next_month)
        ).group_by(Athlete.id).order_by(func.avg(Attendance.effort + Attendance.discipline).desc()).first()

        most_improved[style] = result[0] if result else '—'

    return render_template('home.html',
                           athlete_counts=athlete_counts,
                           session_counts=session_counts,
                           attendance_counts=attendance_counts,
                           top_attendees=top_attendees,
                           most_improved=most_improved)

@app.route('/timetable')
def timetable():
    now = datetime.utcnow()
    end = now + timedelta(days=7)

    sessions = Session.query.filter(
        Session.start_time.between(now, end)
    ).order_by(Session.start_time).all()

    recurring_sessions = Session.query.filter_by(recurring=True).all()
    for s in recurring_sessions:
        next_date = now + timedelta(days=(s.weekday - now.weekday()) % 7)
        repeated = Session(
            name=s.name,
            start_time=next_date.replace(hour=s.start_time.hour, minute=s.start_time.minute),
            duration=s.duration
        )
        repeated.id = None
        sessions.append(repeated)

    athletes = Athlete.query.order_by(Athlete.first_name).all()
    return render_template('timetable.html', sessions=sessions, athletes=athletes)

@app.route('/checkin', methods=['POST'])
def checkin():
    session_id = int(request.form['session_id'])
    athlete_name = request.form['athlete_name']
    effort = int(request.form.get('effort', 0))
    discipline = int(request.form.get('discipline', 0))

    athlete = Athlete.query.filter_by(first_name=athlete_name).first()
    if not athlete:
        flash('Athlete not found.')
        return redirect(url_for('timetable'))

    a = Attendance(athlete_id=athlete.id, session_id=session_id, effort=effort, discipline=discipline)
    db.session.add(a)
    db.session.commit()
    return redirect(url_for('timetable'))

@app.route('/create-session', methods=['GET', 'POST'])
def create_session():
    if request.method == 'POST':
        name = request.form['name']
        session_type = request.form['type']
        start_time = datetime.fromisoformat(request.form['start_time'])
        duration = int(request.form['duration'])
        recurring = request.form['recurring'] == 'yes'
        weekday = start_time.weekday() if recurring else None

        s = Session(
            name=f"{session_type} - {name}",
            start_time=start_time,
            duration=duration,
            recurring=recurring,
            weekday=weekday
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('timetable'))

    now = datetime.utcnow().replace(microsecond=0, second=0)
    default_start = now.isoformat()
    return render_template('create_session.html', default_start=default_start)

@app.route('/athletes')
def athletes():
    all_athletes = Athlete.query.order_by(Athlete.last_name).all()
    return render_template('athletes.html', athletes=all_athletes)

@app.route('/summary')
def summary():
    period = request.args.get('period', 'week')
    now = datetime.utcnow()

    if period == 'week':
        start = now - timedelta(days=7)
    elif period == 'month':
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=90)

    attendances = Attendance.query.filter(Attendance.session.has(Session.start_time >= start)).all()

    stats = {}
    for a in attendances:
        athlete = a.athlete.full_name()
        if athlete not in stats:
            stats[athlete] = {'sessions': 0, 'effort': 0, 'discipline': 0}
        stats[athlete]['sessions'] += 1
        stats[athlete]['effort'] += a.effort
        stats[athlete]['discipline'] += a.discipline

    return render_template('summary.html', stats=stats, period=period)

@app.route('/bulk-delete-athletes', methods=['POST'])
def bulk_delete_athletes():
    athlete_ids = request.form.getlist('athlete_ids')
    for athlete_id in athlete_ids:
        athlete = Athlete.query.get(int(athlete_id))
        if athlete:
            db.session.delete(athlete)
    db.session.commit()
    return redirect(url_for('athletes'))

@app.route('/bulk-delete-sessions', methods=['POST'])
def bulk_delete_sessions():
    session_ids = request.form.getlist('session_ids')
    for session_id in session_ids:
        session = Session.query.get(int(session_id))
        if session:
            db.session.delete(session)
    db.session.commit()
    return redirect(url_for('timetable'))


@app.route('/register-athlete', methods=['GET', 'POST'])
def register_athlete():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        belt = request.form['belt']
        style = request.form['style']
        athlete = Athlete(first_name=first_name, last_name=last_name, belt=belt, style=style)
        db.session.add(athlete)
        db.session.commit()
        return redirect(url_for('athletes'))

    return render_template('register_athlete.html')

# ------------------- Run App -------------------

if __name__ == '__main__':
    app.run(debug=True)
