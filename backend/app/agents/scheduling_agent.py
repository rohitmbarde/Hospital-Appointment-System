from datetime import datetime, timedelta, time, date
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..config import get_settings
from ..models import Appointment, DoctorUnavailable


class SchedulingAgent:
    def __init__(self):
        self.settings = get_settings()

    def _generate_daily_slots(self, target_date: date) -> List[datetime]:
        slots: List[datetime] = []
        start_hour = self.settings.hospital_start_hour
        end_hour = self.settings.hospital_end_hour
        lunch_start = self.settings.lunch_start_hour
        lunch_end = self.settings.lunch_end_hour
        # 30-minute slots
        current = datetime.combine(target_date, time(hour=start_hour, minute=0))
        end_dt = datetime.combine(target_date, time(hour=end_hour, minute=0))
        while current < end_dt:
            if not (lunch_start <= current.hour < lunch_end):
                slots.append(current)
            current += timedelta(minutes=30)
        return slots

    def _is_doctor_unavailable(self, db: Session, doctor_id: int, day: date) -> bool:
        """Check if doctor is unavailable on a specific date.
        Supports both single date and date range (date to end_date)."""
        from sqlalchemy import or_, and_
        
        # Check for exact date match OR if date falls within a range
        query = db.query(DoctorUnavailable).filter(
            DoctorUnavailable.doctor_id == doctor_id
        ).filter(
            or_(
                # Single date match
                and_(
                    DoctorUnavailable.date == day,
                    DoctorUnavailable.end_date.is_(None)
                ),
                # Date range match (date <= day <= end_date)
                and_(
                    DoctorUnavailable.date <= day,
                    DoctorUnavailable.end_date >= day
                ),
                # Backward compatibility: exact match even if end_date exists
                DoctorUnavailable.date == day
            )
        )
        
        return query.count() > 0

    def _is_slot_taken(self, db: Session, doctor_id: int, slot: datetime) -> bool:
        return (
            db.query(Appointment)
            .filter(and_(Appointment.doctor_id == doctor_id, Appointment.appointment_datetime == slot))
            .count()
            > 0
        )

    def get_available_slots(self, db: Session, doctor_id: int, days_ahead: int = 14) -> List[datetime]:
        available: List[datetime] = []
        today = datetime.now().date()
        for delta in range(days_ahead):
            target_date = today + timedelta(days=delta)
            if self._is_doctor_unavailable(db, doctor_id, target_date):
                continue
            daily_slots = self._generate_daily_slots(target_date)
            for slot in daily_slots:
                if slot <= datetime.now():
                    continue
                if not self._is_slot_taken(db, doctor_id, slot):
                    available.append(slot)
        return available

    def book_appointment(
        self,
        db: Session,
        patient_id: int,
        doctor_id: int,
        department_id: int,
        appointment_dt: datetime,
        symptoms: str,
        severity: str | None,
    ) -> Appointment:
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            department_id=department_id,
            appointment_datetime=appointment_dt,
            symptoms=symptoms,
            severity=severity,
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

