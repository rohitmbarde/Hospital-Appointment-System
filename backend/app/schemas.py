from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    email: EmailStr


class PatientOut(BaseModel):
    id: int
    name: str
    age: int
    gender: Optional[str]
    email: EmailStr

    class Config:
        from_attributes = True


class TriageRequest(BaseModel):
    patient: PatientCreate
    symptoms: str = Field(..., min_length=3)


class DoctorRecommendation(BaseModel):
    id: int
    name: str


class TriageResponse(BaseModel):
    patient_id: int
    department_id: int
    department: str
    severity: str
    recommended_doctors: List[DoctorRecommendation]
    available_slots: List[datetime]
    message: Optional[str] = None


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    department_id: int
    appointment_datetime: datetime
    symptoms: str
    severity: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    appointment_datetime: datetime
    doctor_name: str
    department_name: str
    patient_name: str
    severity: Optional[str]
    symptoms: Optional[str]
    email_sent: bool = False

    class Config:
        from_attributes = True


class DoctorUnavailableCreate(BaseModel):
    doctor_id: int
    date: date  # Start date of leave
    end_date: Optional[date] = None  # End date of leave (optional, for date ranges)
    reason: Optional[str] = None


class DoctorUnavailableOut(BaseModel):
    id: int
    doctor_id: int
    doctor_name: str
    date: date
    end_date: Optional[date] = None
    reason: Optional[str]

    class Config:
        from_attributes = True

