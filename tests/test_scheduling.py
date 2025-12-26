import os
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base, Doctor, DoctorUnavailable
from backend.app.agents.scheduling_agent import SchedulingAgent


def setup_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return engine, TestingSessionLocal


def test_slots_exclude_lunch_hour():
    # Configure broad hours to reduce flakiness
    os.environ["HOSPITAL_START_HOUR"] = "8"
    os.environ["HOSPITAL_END_HOUR"] = "18"
    agent = SchedulingAgent()
    _, TestingSessionLocal = setup_db()
    db = TestingSessionLocal()

    doctor = Doctor(name="Dr. Test", department_id=1, is_active=True)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    slots = agent.get_available_slots(db, doctor.id, days_ahead=1)
    lunch_hours = {s.hour for s in slots}
    assert 13 not in lunch_hours

    db.close()


def test_slots_skip_unavailable_day():
    os.environ["HOSPITAL_START_HOUR"] = "8"
    os.environ["HOSPITAL_END_HOUR"] = "18"
    agent = SchedulingAgent()
    _, TestingSessionLocal = setup_db()
    db = TestingSessionLocal()

    doctor = Doctor(name="Dr. Off", department_id=1, is_active=True)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    today = datetime.utcnow().date()
    db.add(DoctorUnavailable(doctor_id=doctor.id, date=today, reason="Leave"))
    db.commit()

    slots = agent.get_available_slots(db, doctor.id, days_ahead=1)
    assert len(slots) == 0

    db.close()

