from typing import Optional
from sqlalchemy.orm import Session
from ..models import SymptomDepartmentMapping
from .llm_client import GroqClient


class SymptomAnalysisResult:
    def __init__(self, is_valid: bool, department: Optional[str], severity: Optional[str], message: Optional[str]):
        self.is_valid = is_valid
        self.department = department
        self.severity = severity
        self.message = message


class SymptomAnalysisAgent:
    def __init__(self):
        # Comprehensive health-related keywords for validation
        self.health_keywords = [
            # General
            "pain", "ache", "hurt", "sick", "ill", "discomfort", "problem", "issue",
            # Specific symptoms
            "fever", "cough", "cold", "flu", "infection", "dizzy", "nausea", "vomit",
            "uneasy", "weak", "fatigue", "tired", "injury", "wound", "cut", "burn",
            # Body parts
            "head", "eye", "eyes", "ear", "nose", "throat", "mouth", "tooth", "teeth",
            "chest", "heart", "lung", "stomach", "abdomen", "belly", "back", "neck",
            "shoulder", "arm", "hand", "leg", "knee", "foot", "skin", "hair", "nail",
            # Symptoms
            "bleeding", "blood", "rash", "swelling", "inflammation", "irritation",
            "itching", "numbness", "tingling", "breathing", "breath", "coughing",
            "sneezing", "runny", "congestion", "discharge",
            # Digestive
            "diarrhea", "constipation", "motions", "loose", "stool", "indigestion",
            "acidity", "heartburn", "gas", "bloating",
            # Neurological  
            "headache", "migraine", "seizure", "paralysis", "stroke", "memory",
            # Mental health
            "anxiety", "stress", "depression", "panic", "sleep", "insomnia",
            # Other
            "fracture", "broken", "sprain", "strain", "allergy", "asthma", "diabetes",
            "pressure", "sugar", "urinary", "urine", "kidney", "liver", "thyroid",
            "vision", "blurred", "hearing", "balance", "vertigo", "palpitation",
            # Women's health / Gynecological
            "period", "periods", "menstrual", "menstruation", "cycle", "irregular",
            "pregnancy", "pregnant", "ovarian", "uterus", "vaginal", "pelvic",
            "cramps", "pcod", "pcos", "fibroids", "endometriosis", "menopause",
            # Mobility / Orthopedic
            "walking", "mobility", "movement", "limping", "stiffness", "joint",
            "muscle", "bone", "spine", "hip", "ankle", "wrist", "elbow",
            # Swallowing / Throat
            "swallow", "swallowing", "dysphagia", "difficulty swallowing", "choking"
        ]
        self.llm_client = GroqClient()

    def _is_health_related(self, symptoms: str) -> bool:
        text = symptoms.lower()
        return any(k in text for k in self.health_keywords)
    
    def _detect_severity(self, symptoms: str) -> str:
        """
        Intelligently detect severity level based on symptom keywords.
        Returns: "High", "Medium", or "Low"
        """
        text = symptoms.lower()
        
        # HIGH SEVERITY - Emergency/Urgent symptoms
        high_severity_keywords = [
            "bleeding", "blood", "hemorrhage",
            "chest pain", "heart attack", "cardiac",
            "shortness of breath", "can't breathe", "choking",
            "unconscious", "fainting", "collapsed",
            "seizure", "convulsion", "fits",
            "severe", "intense", "unbearable", "excruciating",
            "emergency", "urgent", "critical",
            "fracture", "broken bone",
            "stroke", "paralysis", "facial drooping",
            "suicide", "self harm",
            "high fever", "very high",
            "sharp pain", "crushing pain"
        ]
        
        # LOW SEVERITY - Minor/Common symptoms
        low_severity_keywords = [
            "mild", "slight", "minor", "little",
            "common cold", "runny nose",
            "mild cough", "slight cough",
            "dandruff", "hair fall", "hair loss",
            "mild rash", "minor rash",
            "small cut", "bruise",
            "mild headache"
        ]
        
        # Check for high severity
        if any(keyword in text for keyword in high_severity_keywords):
            return "High"
        
        # Check for low severity
        if any(keyword in text for keyword in low_severity_keywords):
            return "Low"
        
        # MEDIUM SEVERITY - Default for most symptoms
        return "Medium"

    def analyze(self, db: Session, symptoms: str) -> SymptomAnalysisResult:
        text = symptoms.lower()
        # Validate that symptoms appear health related
        if not self._is_health_related(text):
            return SymptomAnalysisResult(False, None, None, "Please mention health related symptoms")

        # Get available departments from database dynamically
        from ..models import Department
        available_depts = db.query(Department).all()
        dept_names = [dept.name for dept in available_depts]
        
        # PRIMARY: Use LLM for intelligent natural language understanding
        llm_result = self.llm_client.interpret_symptoms(symptoms, available_departments=dept_names)
        
        if llm_result:
            # Verify LLM result exists in DB
            dept = db.query(Department).filter(Department.name.ilike(f"%{llm_result}%")).first()
            if dept:
                # Auto-detect severity
                severity = self._detect_severity(text)
                return SymptomAnalysisResult(True, dept.name, severity, None)
        
        # FALLBACK: Try rule-based mapping only if LLM fails
        mapping_rows = db.query(SymptomDepartmentMapping).all()
        for row in mapping_rows:
            if row.symptom_keyword.lower() in text:
                severity = self._detect_severity(text) or row.default_severity or "Medium"
                return SymptomAnalysisResult(True, row.department.name, severity, None)

        # LAST RESORT: General Medicine fallback
        general_med = db.query(Department).filter(Department.name.ilike("%General Medicine%")).first()
        if general_med:
            return SymptomAnalysisResult(
                True, 
                general_med.name, 
                "Medium", 
                "⚠️ We don't have a specialist for your specific symptoms. You've been referred to General Medicine, where our doctors can assess and refer you to an external specialist if needed."
            )
        
        return SymptomAnalysisResult(
            False, 
            None, 
            None, 
            "Unfortunately, we don't have a specialist for your symptoms in our hospital. Please visit a general hospital or consult with your family doctor."
        )

