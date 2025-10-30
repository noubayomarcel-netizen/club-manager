from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, current_user
from sqlalchemy import func

from extensions import db, migrate, login_manager
from models import User, Athlete, Session, Attendance, Announcement

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------- Routes -------------------
@app.route('/health')
def health():
    return "OK", 200

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

    # ✅ Athletes per session group
    group_counts = {
        style: Athlete.query.filter_by(group=style).count()
        for style in styles
    }

    # ✅ Sessions per group this month
    session_counts = {
        style: Session.query.filter(
            Session.name.contains(style),
            Session.date.between(start_of_month, next_month)
        ).count()
        for style in styles
    }

    # ✅ Attendance per group this month
    attendance_counts = {
        style: db.session.query(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.date.between(start_of_month, next_month)
        ).count()
        for style in styles
    }

    # ✅ Top attendee per group
    top_attendees = {}
    for style in styles:
        result = db.session.query(
            Athlete.first_name,
            Athlete.last_name,
            func.count(Attendance.id).label('attendance_count')
        ).join(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.date.between(start_of_month, next_month)
        ).group_by(Athlete.id).order_by(func.count(Attendance.id).desc()).first()

        top_attendees[style] = f"{result.first_name} {result.last_name}" if result else '—'

    # ✅ Most improved per group
    most_improved = {}
    for style in styles:
        result = db.session.query(
            Athlete.first_name,
            func.avg(Attendance.effort + Attendance.discipline).label('score')
        ).join(Attendance).join(Session).filter(
            Session.name.contains(style),
            Session.date.between(start_of_month, next_month)
        ).group_by(Athlete.id).order_by(func.avg(Attendance.effort + Attendance.discipline).desc()).first()

        most_improved[style] = result[0] if result else '—'

    return render_template('home.html',
                           group_counts=group_counts,
                           session_counts=session_counts,
                           attendance_counts=attendance_counts,
                           top_attendees=top_attendees,
                           most_improved=most_improved)
 

@app.route('/timetable')
def timetable():
    now = datetime.today()
    sessions = Session.query.filter(Session.date >= now).order_by(Session.date).all()
    athletes = Athlete.query.order_by(Athlete.last_name).all()

    grouped = {}
    for s in sessions:
        if s.date:
            weekday = s.date.strftime("%A")
        else:
            weekday_map = {
                "Monday": 0, "Tuesday": 1, "Wednesday": 2,
                "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
            }
            target_weekday = weekday_map.get(s.weekday, 0)
            next_date = now + timedelta(days=(target_weekday - now.weekday()) % 7)
            weekday = next_date.strftime("%A")

        grouped.setdefault(weekday, []).append(s)

    return render_template("timetable.html", grouped=grouped, sessions=sessions, athletes=athletes)

@app.route('/checkin', methods=['POST'])
def checkin():
    session_id = int(request.form['session_id'])
    athlete_name = request.form['athlete_name']
    effort = int(request.form.get('effort', 0))
    discipline = int(request.form.get('discipline', 0))

    athlete = Athlete.query.filter_by(first_name=athlete_name).first()
    if not athlete:
        flash('Athlete not found.', 'danger')
        return redirect(url_for('timetable'))

    a = Attendance(athlete_id=athlete.id, session_id=session_id, effort=effort, discipline=discipline)
    db.session.add(a)
    db.session.commit()
    flash('Check-in recorded.', 'success')
    return redirect(url_for('timetable'))

from datetime import datetime, timedelta  

@app.route('/create-session', methods=['GET', 'POST'])
def create_session():
    if request.method == 'POST':
        name = request.form.get('name')
        session_type = request.form.get('type')
        start_date = request.form.get('start_date')  
        start_time = request.form.get('start_time')  

        if not start_date or not start_time:
            flash("Start date and time are required.", "danger")
            return redirect(url_for('create_session'))

        try:
            combined = f"{start_date}T{start_time}"  
            date = datetime.fromisoformat(combined)
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return redirect(url_for('create_session'))

        recurring = request.form.get('recurring') == 'yes'
        weekday = date.weekday() if recurring else None

        s = Session(
            name=f"{session_type} - {name}",
            date=date,
            recurring=recurring,
            weekday=weekday,
            location=request.form.get('location', 'Mat A'),
            coach_name=request.form.get('coach_name', 'Coach Eric')
        )
        db.session.add(s)
        db.session.commit()
        flash('Session created.', 'success')
        return redirect(url_for('timetable'))

    now = datetime.utcnow().replace(microsecond=0, second=0)
    default_start = now.isoformat()
    return render_template('create_session.html', default_start=default_start)

@app.route('/session/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    session = Session.query.get_or_404(session_id)
    form = SessionForm(obj=session)
    if form.validate_on_submit():
        form.populate_obj(session)
        db.session.commit()
        flash('Session updated.', 'success')
        return redirect(url_for('timetable'))
    return render_template('edit_session.html', form=form)

@app.route('/delete-session', methods=['POST'])
def delete_session():
    session_id = int(request.form['session_id'])
    session = Session.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    flash("Session deleted.", "warning")
    return redirect(url_for('timetable'))

@app.route('/bulk-delete-sessions', methods=['POST'])
def bulk_delete_sessions():
    session_ids = request.form.getlist('session_ids')
    for session_id in session_ids:
        session = Session.query.get(int(session_id))
        if session:
            db.session.delete(session)
    db.session.commit()
    flash(f"{len(session_ids)} sessions deleted.", "warning")
    return redirect(url_for('timetable'))

from datetime import datetime, date
# ------------------- Routes -------------------

from datetime import date

@app.route('/athletes')
def athletes():
    belt = request.args.get('belt')
    gender = request.args.get('gender')
    group = request.args.get('group')

    query = Athlete.query

    # ✅ Filter by belt and gender if provided
    if belt:
        query = query.filter_by(belt=belt)
    if gender:
        query = query.filter_by(gender=gender)

    # ✅ Filter by discipline group directly
    if group:
        query = query.filter_by(group=group)

    athletes = query.order_by(Athlete.last_name).all()
    return render_template('athletes.html', athletes=athletes)


@app.route('/update_athlete', methods=['POST'])
def update_athlete():
    athlete = Athlete.query.get(request.form['athlete_id'])
    athlete.belt = request.form['belt']
    weight = request.form.get('weight')
    athlete.weight = float(weight) if weight else None
    athlete.gender = request.form['gender']
    dob = request.form['date_of_birth']
    athlete.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
    db.session.commit()
    flash("✅ Athlete updated.", "success")
    return redirect(url_for('athletes'))

@app.route('/edit-athlete/<int:athlete_id>', methods=['GET', 'POST'])
def edit_athlete(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)

    if request.method == 'POST':
        athlete.first_name = request.form['first_name']
        athlete.last_name = request.form['last_name']
        athlete.belt = request.form['belt']
        athlete.weight = request.form.get('weight', type=float)
        athlete.gender = request.form.get('gender')
        dob = request.form.get('date_of_birth')
        athlete.date_of_birth = datetime.strptime(dob, '%Y-%m-%d') if dob else None

        db.session.commit()
        return redirect(url_for('athletes'))

    return render_template('edit_athlete.html', athlete=athlete)

@app.route('/delete-athlete/<int:athlete_id>', methods=['POST'])
def delete_athlete(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)
    db.session.delete(athlete)
    db.session.commit()
    return redirect(url_for('athletes'))

@app.route('/bulk-delete-athletes', methods=['POST'])
def bulk_delete_athletes():
    athlete_ids = request.form.getlist('athlete_ids')
    for athlete_id in athlete_ids:
        athlete = Athlete.query.get(int(athlete_id))
        if athlete:
            db.session.delete(athlete)
    db.session.commit()
    flash(f"{len(athlete_ids)} athletes deleted.", "warning")
    return redirect(url_for('athletes'))

@app.route('/register-athlete', methods=['GET', 'POST'])
def register_athlete():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        belt = request.form.get('belt')
        dob = request.form.get('date_of_birth') or None
        weight = request.form.get('weight') or None
        gender = request.form.get('gender') or None
        group = request.form.get('group') or None  # ✅ New discipline group

        # ✅ Validate required fields only
        if not first_name or not last_name or not belt or not group:
            flash("First name, last name, belt, and discipline group are required.", "danger")
            return redirect(url_for('register_athlete'))

        # ✅ Convert optional fields if provided
        from datetime import datetime
        if dob:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        if weight:
            weight = float(weight)

        # ✅ Create athlete object
        athlete = Athlete(
            first_name=first_name,
            last_name=last_name,
            belt=belt,
            date_of_birth=dob,
            weight=weight,
            gender=gender,
            group=group
        )

        db.session.add(athlete)
        db.session.commit()
        flash("✅ Athlete registered successfully.", "success")
        return redirect(url_for('athletes'))

    # GET request fallback
    return render_template('register_athlete.html')

# ------------------- Run App -------------------

if __name__ == '__main__':
    app.run(debug=True)
