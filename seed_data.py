from app import app, db
from models import User, Athlete, Session, Attendance, Announcement
from datetime import datetime, timedelta

with app.app_context():
    # Optional: Clear existing data
    db.drop_all()
    db.create_all()

    # Create coach user
    if not User.query.filter_by(username='coach').first():
        coach = User(username='coach', password='pass123', role='coach')
        db.session.add(coach)

    # Create athletes
    athletes = [
        Athlete(first_name='John', last_name='Doe', belt='Blue', style='Adults BJJ'),
        Athlete(first_name='Maria', last_name='Lopez', belt='White', style='Kids BJJ'),
        Athlete(first_name='Kojo', last_name='Mensah', belt='Green', style='Sheen Wrestling'),
        Athlete(first_name='Amina', last_name='Khan', belt='Yellow', style='LOGA MMA'),
        Athlete(first_name='Liam', last_name='Smith', belt='Orange', style='Kids Wrestling'),
    ]
    db.session.add_all(athletes)

    # Create sessions
    now = datetime.utcnow()
    sessions = [
        Session(name='Adults BJJ - Guard Passing', start_time=now - timedelta(days=2), duration=60),
        Session(name='Kids BJJ - Takedowns', start_time=now - timedelta(days=1), duration=45),
        Session(name='Sheen Wrestling - Conditioning', start_time=now, duration=90, recurring=True, weekday=now.weekday()),
        Session(name='LOGA MMA - Striking', start_time=now + timedelta(days=1), duration=60),
        Session(name='Kids Wrestling - Drills', start_time=now + timedelta(days=2), duration=50),
    ]
    db.session.add_all(sessions)

    # Create attendance records
    attendances = [
        Attendance(athlete_id=1, session_id=1, effort=8, discipline=7),
        Attendance(athlete_id=2, session_id=2, effort=9, discipline=8),
        Attendance(athlete_id=3, session_id=3, effort=7, discipline=6),
        Attendance(athlete_id=4, session_id=4, effort=10, discipline=9),
        Attendance(athlete_id=5, session_id=5, effort=6, discipline=7),
        Attendance(athlete_id=1, session_id=4, effort=9, discipline=8),
        Attendance(athlete_id=2, session_id=1, effort=7, discipline=6),
    ]
    db.session.add_all(attendances)

    # Create announcements
    announcements = [
        Announcement(title="Welcome to the Club!", content="We're excited to launch our new training season."),
        Announcement(title="Holiday Schedule", content="No classes on public holidays. Check the timetable for updates."),
    ]
    db.session.add_all(announcements)

    db.session.commit()
    print("✅ Sample data seeded successfully.")
