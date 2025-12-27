from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Time, Enum, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    appointments = relationship("Appointment", back_populates="patient")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    doctors = relationship("Doctor", back_populates="department")
    appointments = relationship("Appointment", back_populates="department")
    symptom_mappings = relationship("SymptomDepartmentMapping", back_populates="department")


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    unavailable = relationship("DoctorUnavailable", back_populates="doctor")


class DoctorUnavailable(Base):
    __tablename__ = "doctor_unavailable"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(Date, nullable=False)  # Start date (kept for backward compatibility)
    end_date = Column(Date, nullable=True)  # End date for leave range
    reason = Column(String, nullable=True)

    doctor = relationship("Doctor", back_populates="unavailable")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False)
    severity = Column(String, nullable=True)
    symptoms = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    department = relationship("Department", back_populates="appointments")


class SymptomDepartmentMapping(Base):
    __tablename__ = "symptom_department_mapping"
    id = Column(Integer, primary_key=True, index=True)
    symptom_keyword = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    default_severity = Column(String, nullable=True)

    department = relationship("Department", back_populates="symptom_mappings")

