"""
Seed the database with baseline departments, doctors, and symptom mappings.
Run: `python -m backend.app.seed_data`
Requires: DATABASE_URL env pointing to your Postgres instance.
"""

from datetime import date
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import Department, Doctor, SymptomDepartmentMapping, DoctorUnavailable


DEPARTMENTS = [
    "General Medicine",
    "Cardiology",
    "Neurology",
    "Pediatrics",
    "Orthopedics",
    "Dermatology",
    "ENT",
    "Psychiatry",
]

DOCTORS = [
    ("General Medicine", "Dr. Asha Menon", "asha.menon@example.com"),
    ("Cardiology", "Dr. Raj Patel", "raj.patel@example.com"),
    ("Neurology", "Dr. Neha Iyer", "neha.iyer@example.com"),
    ("Pediatrics", "Dr. Arjun Rao", "arjun.rao@example.com"),
    ("Orthopedics", "Dr. Karan Singh", "karan.singh@example.com"),
    ("Dermatology", "Dr. Meera Shah", "meera.shah@example.com"),
    ("ENT", "Dr. Farah Khan", "farah.khan@example.com"),
    ("Psychiatry", "Dr. Vivek Gupta", "vivek.gupta@example.com"),
]

SYMPTOM_MAPPINGS = [
    ("chest pain", "Cardiology", "High"),
    ("chest", "Cardiology", "High"),
    ("shortness of breath", "Cardiology", "High"),
    ("breathing", "Cardiology", "High"),
    ("headache", "Neurology", "Medium"),
    ("migraine", "Neurology", "Medium"),
    ("head pain", "Neurology", "Medium"),
    ("fever", "General Medicine", "Medium"),
    ("cough", "General Medicine", "Low"),
    ("cold", "General Medicine", "Low"),
    ("vomiting", "General Medicine", "Medium"),
    ("diarrhea", "General Medicine", "Medium"),
    ("loose motions", "General Medicine", "Medium"),
    ("motions", "General Medicine", "Medium"),
    ("stomach pain", "General Medicine", "Medium"),
    ("stomach ache", "General Medicine", "Medium"),
    ("abdomen pain", "General Medicine", "Medium"),
    ("indigestion", "General Medicine", "Low"),
    ("acidity", "General Medicine", "Low"),
    ("constipation", "General Medicine", "Low"),
    ("nausea", "General Medicine", "Low"),
    ("bleeding", "General Medicine", "High"),
    ("blood", "General Medicine", "High"),
    ("rash", "Dermatology", "Low"),
    ("skin", "Dermatology", "Low"),
    ("joint pain", "Orthopedics", "Medium"),
    ("knee pain", "Orthopedics", "Medium"),
    ("leg pain", "Orthopedics", "Medium"),
    ("back pain", "Orthopedics", "Medium"),
    ("fracture", "Orthopedics", "High"),
    ("difficulty walking", "Orthopedics", "Medium"),
    ("walking", "Orthopedics", "Medium"),
    ("mobility", "Orthopedics", "Medium"),
    ("limping", "Orthopedics", "Medium"),
    ("stiffness", "Orthopedics", "Medium"),
    ("joint stiffness", "Orthopedics", "Medium"),
    ("muscle pain", "Orthopedics", "Medium"),
    ("hip pain", "Orthopedics", "Medium"),
    ("ankle pain", "Orthopedics", "Medium"),
    ("wrist pain", "Orthopedics", "Medium"),
    ("elbow pain", "Orthopedics", "Medium"),
    ("spine", "Orthopedics", "Medium"),
    ("ear pain", "ENT", "Low"),
    ("ear", "ENT", "Low"),
    ("sore throat", "ENT", "Low"),
    ("throat", "ENT", "Low"),
    ("nose", "ENT", "Low"),
    ("mouth", "ENT", "Medium"),
    ("bleeding from mouth", "ENT", "High"),
    ("nose bleeding", "ENT", "Medium"),
    ("difficulty swallowing", "ENT", "Medium"),
    ("swallowing", "ENT", "Medium"),
    ("dysphagia", "ENT", "Medium"),
    ("choking", "ENT", "High"),
    ("throat pain", "ENT", "Medium"),
    ("anxiety", "Psychiatry", "Medium"),
    ("depression", "Psychiatry", "Medium"),
    ("stress", "Psychiatry", "Medium"),
    ("uneasy and low", "Psychiatry", "Medium"),
    ("child fever", "Pediatrics", "Medium"),
    ("child cough", "Pediatrics", "Medium"),
    ("eye", "General Medicine", "Medium"),
    ("eyes", "General Medicine", "Medium"),
    ("vision", "General Medicine", "Medium"),
    ("blurred vision", "General Medicine", "Medium"),
    ("eye pain", "General Medicine", "Medium"),
    ("eye irritation", "General Medicine", "Low"),
    ("hair fall", "General Medicine", "Low"),
    ("hair loss", "General Medicine", "Low"),
    ("baldness", "General Medicine", "Low"),
    ("dandruff", "General Medicine", "Low"),
    # Women's health / Gynecological symptoms (mapped to General Medicine)
    ("irregular periods", "General Medicine", "Medium"),
    ("period", "General Medicine", "Medium"),
    ("periods", "General Medicine", "Medium"),
    ("menstrual", "General Medicine", "Medium"),
    ("menstruation", "General Medicine", "Medium"),
    ("pelvic pain", "General Medicine", "Medium"),
    ("cramps", "General Medicine", "Low"),
    ("menstrual cramps", "General Medicine", "Medium"),
    ("vaginal", "General Medicine", "Medium"),
    ("pregnancy", "General Medicine", "Medium"),
    ("pcod", "General Medicine", "Medium"),
    ("pcos", "General Medicine", "Medium"),
]

UNAVAILABILITY = [
    # Example: mark a doctor unavailable tomorrow
    # ("Dr. Raj Patel", date.today() + timedelta(days=1), "Conference"),
]


def get_or_create_department(session: Session, name: str) -> Department:
    dept = session.query(Department).filter(Department.name == name).first()
    if dept:
        return dept
    dept = Department(name=name)
    session.add(dept)
    session.commit()
    session.refresh(dept)
    return dept


def get_or_create_doctor(session: Session, name: str, dept: Department, email: str | None) -> Doctor:
    doc = session.query(Doctor).filter(Doctor.name == name).first()
    if doc:
        return doc
    doc = Doctor(name=name, department_id=dept.id, email=email, is_active=True)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


def add_symptom_mapping(session: Session, keyword: str, dept: Department, severity: str | None):
    existing = (
        session.query(SymptomDepartmentMapping)
        .filter(SymptomDepartmentMapping.symptom_keyword == keyword)
        .first()
    )
    if existing:
        return
    mapping = SymptomDepartmentMapping(symptom_keyword=keyword, department_id=dept.id, default_severity=severity)
    session.add(mapping)
    session.commit()


def add_unavailability(session: Session, doctor: Doctor, day: date, reason: str | None):
    exists = (
        session.query(DoctorUnavailable)
        .filter(DoctorUnavailable.doctor_id == doctor.id, DoctorUnavailable.date == day)
        .first()
    )
    if exists:
        return
    session.add(DoctorUnavailable(doctor_id=doctor.id, date=day, reason=reason))
    session.commit()


def main():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        dept_map = {}
        for dept_name in DEPARTMENTS:
            dept_map[dept_name] = get_or_create_department(session, dept_name)

        doctor_map = {}
        for dept_name, doc_name, email in DOCTORS:
            doctor_map[doc_name] = get_or_create_doctor(session, doc_name, dept_map[dept_name], email)

        for keyword, dept_name, severity in SYMPTOM_MAPPINGS:
            add_symptom_mapping(session, keyword, dept_map[dept_name], severity)

        for doc_name, day, reason in UNAVAILABILITY:
            if doc_name in doctor_map:
                add_unavailability(session, doctor_map[doc_name], day, reason)

        print("Seed data inserted/updated.")
    finally:
        session.close()


if __name__ == "__main__":
    main()

