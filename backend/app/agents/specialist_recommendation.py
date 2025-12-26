from typing import List
from sqlalchemy.orm import Session
from ..models import Department, Doctor


class SpecialistRecommendationAgent:
    def recommend(self, db: Session, department_name: str, patient_age: int) -> List[Doctor]:
        """
        Map symptoms -> department -> doctors, enforcing pediatrics rule.
        Only returns active doctors that match the department.
        """
        target_department_name = department_name
        if patient_age < 13:
            target_department_name = "Pediatrics"

        department = db.query(Department).filter(Department.name.ilike(target_department_name)).first()
        if not department:
            return []

        doctors = (
            db.query(Doctor)
            .filter(Doctor.department_id == department.id)
            .filter(Doctor.is_active.is_(True))
            .all()
        )
        return doctors

