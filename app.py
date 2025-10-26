from flask import Flask, render_template, request, redirect, url_for
from extensions import db, migrate
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        import models  # registers Athlete, Session, Attendance

    return app

app = create_app()

# Import models after app is created
from models import Athlete, Session, Attendance

# ROUTES

@app.route('/athletes')
def athletes():
    athletes = Athlete.query.order_by(Athlete.last_name).all()
    return render_template('athletes.html', athletes=athletes)

@app.route('/timetable')
def timetable():
    now = datetime.utcnow()
    end = now + timedelta(days=7)
    sessions = Session.query.filter(Session.start_time.between(now, end)).order_by(Session.start_time).all()
    athlete_id = request.args.get('athlete')
    return render_template('timetable.html', sessions=sessions, athlete_id=athlete_id)

@app.route('/checkin', methods=['POST'])
def checkin():
    athlete_id = int(request.form['athlete_id'])
    session_id = int(request.form['session_id'])
    effort = int(request.form.get('effort', 0))
    discipline = int(request.form.get('discipline', 0))
    a = Attendance(athlete_id=athlete_id, session_id=session_id, effort=effort, discipline=discipline)
    db.session.add(a)
    db.session.commit()
    return redirect(request.referrer or url_for('timetable'))

@app.route('/summary')
def summary():
    period = request.args.get('period', 'week')
    date_str = request.args.get('date')
    ref = datetime.utcnow().date() if not date_str else datetime.fromisoformat(date_str).date()

    if period == 'week':
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=6)
    elif period == 'month':
        start = ref.replace(day=1)
        last_day = calendar.monthrange(ref.year, ref.month)[1]
        end = ref.replace(day=last_day)
    else:
        start = ref.replace(month=1, day=1)
        end = ref.replace(month=12, day=31)

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    rows = db.session.query(
        Attendance.athlete_id,
        db.func.count(Attendance.id).label('attended'),
        db.func.avg(Attendance.effort).label('avg_effort'),
        db.func.avg(Attendance.discipline).label('avg_discipline')
    ).filter(Attendance.check_in_time.between(start_dt, end_dt)).group_by(Attendance.athlete_id).all()

    athlete_map = {a.id: a for a in Athlete.query.filter(Athlete.id.in_([r.athlete_id for r in rows])).all()}
    summary = []
    for r in rows:
        athlete = athlete_map.get(r.athlete_id)
        summary.append({
            'athlete_id': r.athlete_id,
            'name': athlete.full_name() if athlete else 'Unknown',
            'attended': int(r.attended),
            'avg_effort': round(r.avg_effort or 0, 2),
            'avg_discipline': round(r.avg_discipline or 0, 2),
        })

    return render_template('summary.html', summary=summary, period=period, start=start, end=end)

# Optional fallback: create tables directly if CLI fails
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
@app.route('/register-athlete', methods=['GET', 'POST'])
def register_athlete():
    if request.method == 'POST':
        a = Athlete(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            belt=request.form['belt']
        )
        db.session.add(a)
        db.session.commit()
        return redirect(url_for('athletes'))
    return render_template('register_athlete.html')

@app.route('/create-session', methods=['GET', 'POST'])
def create_session():
    if request.method == 'POST':
        s = Session(
            name=request.form['name'],
            start_time=datetime.fromisoformat(request.form['start_time']),
            duration_minutes=int(request.form['duration'])
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('timetable'))
    return render_template('create_session.html')
