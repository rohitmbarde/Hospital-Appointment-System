from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..config import get_settings
from ..models import Appointment, Doctor, Department, Patient, DoctorUnavailable
from ..schemas import DoctorUnavailableCreate, DoctorUnavailableOut, AppointmentOut, PatientOut

router = APIRouter()
settings = get_settings()


def admin_guard(x_admin_password: str = Header(...)):
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")


@router.get("/appointments", response_model=List[AppointmentOut], dependencies=[Depends(admin_guard)])
def list_appointments(
    doctor_name: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Appointment, Doctor, Department, Patient)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(Department, Appointment.department_id == Department.id)
        .join(Patient, Appointment.patient_id == Patient.id)
    )
    if doctor_name:
        query = query.filter(Doctor.name.ilike(f"%{doctor_name}%"))
    if department:
        query = query.filter(Department.name.ilike(f"%{department}%"))

    rows = query.all()
    result: List[AppointmentOut] = []
    for appointment, doctor, dept, patient in rows:
        result.append(
            AppointmentOut(
                id=appointment.id,
                appointment_datetime=appointment.appointment_datetime,
                doctor_name=doctor.name,
                department_name=dept.name,
                patient_name=patient.name,
                severity=appointment.severity,
                symptoms=appointment.symptoms,
                email_sent=False,  # Default value for admin view
            )
        )
    return result


@router.get("/doctor-unavailable", response_model=List[DoctorUnavailableOut], dependencies=[Depends(admin_guard)])
def list_unavailability(db: Session = Depends(get_db)):
    rows = db.query(DoctorUnavailable, Doctor).join(Doctor, DoctorUnavailable.doctor_id == Doctor.id).all()
    result = []
    for unavailable, doctor in rows:
        result.append(
            DoctorUnavailableOut(
                id=unavailable.id,
                doctor_id=unavailable.doctor_id,
                doctor_name=doctor.name,
                date=unavailable.date,
                reason=unavailable.reason
            )
        )
    return result


@router.post("/doctor-unavailable", response_model=DoctorUnavailableOut, dependencies=[Depends(admin_guard)])
def add_unavailability(payload: DoctorUnavailableCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    record = DoctorUnavailable(
        doctor_id=payload.doctor_id, 
        date=payload.date,
        reason=payload.reason
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # Return with doctor_name populated
    return DoctorUnavailableOut(
        id=record.id,
        doctor_id=record.doctor_id,
        doctor_name=doctor.name,
        date=record.date,
        reason=record.reason
    )


@router.get("/patients", response_model=List[PatientOut], dependencies=[Depends(admin_guard)])
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return patients


@router.get("/doctors", dependencies=[Depends(admin_guard)])
def list_doctors(db: Session = Depends(get_db)):
    """Get list of all doctors with their departments"""
    doctors = (
        db.query(Doctor, Department)
        .join(Department, Doctor.department_id == Department.id)
        .all()
    )
    result = []
    for doctor, dept in doctors:
        result.append({
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "department": dept.name,
            "is_active": doctor.is_active
        })
    return result

