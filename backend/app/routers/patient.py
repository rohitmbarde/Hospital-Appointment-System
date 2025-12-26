from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..schemas import (
    TriageRequest,
    TriageResponse,
    AppointmentCreate,
    AppointmentOut,
    PatientCreate,
    DoctorRecommendation,
)
from ..models import Patient, Doctor, Department
from ..agents.symptom_analysis import SymptomAnalysisAgent
from ..agents.specialist_recommendation import SpecialistRecommendationAgent
from ..agents.scheduling_agent import SchedulingAgent
from ..services.email_service import EmailService

router = APIRouter()

symptom_agent = SymptomAnalysisAgent()
specialist_agent = SpecialistRecommendationAgent()
scheduling_agent = SchedulingAgent()
email_service = EmailService()


def _get_or_create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    patient = db.query(Patient).filter(Patient.email == patient_data.email).first()
    if patient:
        return patient
    patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender,
        email=patient_data.email,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest, db: Session = Depends(get_db)):
    analysis = symptom_agent.analyze(db, request.symptoms)
    if not analysis.is_valid or not analysis.department:
        raise HTTPException(status_code=400, detail=analysis.message or "Invalid symptoms")

    patient = _get_or_create_patient(db, request.patient)

    mapped_department = analysis.department.strip()
    department = db.query(Department).filter(Department.name.ilike(mapped_department)).first()
    if not department:
        # Try a contains match in case the mapper/LLM adds extra words (e.g., "Psychiatry department")
        department = db.query(Department).filter(Department.name.ilike(f"%{mapped_department}%")).first()
    if not department:
        raise HTTPException(status_code=400, detail="Mapped department not found in database")

    doctors = specialist_agent.recommend(db, department.name, patient.age)
    if not doctors:
        raise HTTPException(status_code=400, detail="No available doctors for the department")

    # Pick the first recommended doctor to generate slots
    primary_doctor = doctors[0]
    slots = scheduling_agent.get_available_slots(db, primary_doctor.id)
    if not slots:
        raise HTTPException(status_code=400, detail="No available slots for the selected doctor")

    return TriageResponse(
        patient_id=patient.id,
        department_id=department.id,
        department=analysis.department,
        severity=analysis.severity or "Medium",
        recommended_doctors=[DoctorRecommendation(id=d.id, name=d.name) for d in doctors],
        available_slots=slots[:10],
        message=analysis.message,
    )


@router.post("/appointments", response_model=AppointmentOut)
async def book_appointment(request: AppointmentCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == request.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    department = db.query(Department).filter(Department.id == request.department_id).first()
    if not department or department.id != doctor.department_id:
        raise HTTPException(status_code=400, detail="Doctor does not belong to the department")

    patient = db.query(Patient).filter(Patient.id == request.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    slot_dt = request.appointment_datetime
    available_slots = scheduling_agent.get_available_slots(db, doctor.id)
    if slot_dt not in available_slots:
        raise HTTPException(status_code=400, detail="Selected slot is not available")

    appointment = scheduling_agent.book_appointment(
        db,
        patient_id=patient.id,
        doctor_id=doctor.id,
        department_id=department.id,
        appointment_dt=slot_dt,
        symptoms=request.symptoms,
        severity=request.severity,
    )

    email_sent = await email_service.send_confirmation(
        to_email=patient.email,
        patient_name=patient.name,
        doctor_name=doctor.name,
        department_name=department.name,
        appointment_dt=slot_dt.isoformat(),
        booking_id=appointment.id,
    )

    return AppointmentOut(
        id=appointment.id,
        appointment_datetime=appointment.appointment_datetime,
        doctor_name=doctor.name,
        department_name=department.name,
        patient_name=patient.name,
        severity=appointment.severity,
        symptoms=appointment.symptoms,
        email_sent=email_sent,
    )

