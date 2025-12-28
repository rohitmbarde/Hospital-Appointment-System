# 🔧 Technical Documentation - Hospital Appointment System

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Backend Architecture](#backend-architecture)
3. [AI Agent System](#ai-agent-system)
4. [Database Design](#database-design)
5. [API Reference](#api-reference)
6. [Frontend Architecture](#frontend-architecture)
7. [Configuration Management](#configuration-management)
8. [Deployment Guide](#deployment-guide)

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                      │
│                       (Streamlit Frontend)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Patient Portal  │  │ Admin Dashboard │  │  Triage System  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└────────────────────────────┬──────────────────────────────────────┘
                             │ HTTP/REST API
┌────────────────────────────▼──────────────────────────────────────┐
│                      APPLICATION LAYER                            │
│                      (FastAPI Backend)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ROUTERS                                │   │
│  │  ┌──────────────┐              ┌──────────────┐         │   │
│  │  │ Patient API  │              │  Admin API   │         │   │
│  │  └──────────────┘              └──────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   AGENT LAYER                             │   │
│  │  ┌────────────────────┐  ┌─────────────────────┐        │   │
│  │  │ Symptom Analysis   │  │  Scheduling Agent   │        │   │
│  │  │      Agent         │  │                     │        │   │
│  │  │                    │  │                     │        │   │
│  │  │  ┌──────────────┐ │  │  ┌──────────────┐  │        │   │
│  │  │  │ LLM Client   │ │  │  │ Slot Manager │  │        │   │
│  │  │  │ (Groq API)   │ │  │  │              │  │        │   │
│  │  │  └──────────────┘ │  │  └──────────────┘  │        │   │
│  │  │                    │  │                     │        │   │
│  │  │  ┌──────────────┐ │  │  ┌──────────────┐  │        │   │
│  │  │  │ Rule Engine  │ │  │  │Leave Checker │  │        │   │
│  │  │  │ (Fallback)   │ │  │  │              │  │        │   │
│  │  │  └──────────────┘ │  │  └──────────────┘  │        │   │
│  │  └────────────────────┘  └─────────────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   DATA LAYER                              │   │
│  │  ┌────────────────────┐  ┌─────────────────────┐        │   │
│  │  │  SQLAlchemy ORM    │  │   Pydantic Schemas  │        │   │
│  │  └────────────────────┘  └─────────────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬──────────────────────────────────────┘
                             │ Database Queries
┌────────────────────────────▼──────────────────────────────────────┐
│                     DATABASE LAYER                                │
│                    (PostgreSQL 14+)                               │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────────┐          │
│  │ Departments  │  │  Doctors  │  │   Appointments   │          │
│  └──────────────┘  └───────────┘  └──────────────────┘          │
│  ┌──────────────┐  ┌───────────────────────────────────┐        │
│  │ Doctor Leave │  │  Symptom Dept Mapping            │        │
│  └──────────────┘  └───────────────────────────────────┘        │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                               │
│  ┌──────────────┐  ┌───────────┐                                 │
│  │  Groq API    │  │  Gmail    │                                 │
│  │  (LLM)       │  │  SMTP     │                                 │
│  └──────────────┘  └───────────┘                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## Backend Architecture

### FastAPI Application Structure

#### 1. Main Application (`backend/app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import admin, patient

app = FastAPI(
    title="Hospital Appointment System",
    version="1.0",
    description="AI-powered multi-agent appointment system"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(patient.router, prefix="/api/patient", tags=["Patient"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "Hospital Appointment System API"}
```

#### 2. Database Models (`backend/app/models.py`)

**Key Models:**

```python
class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    doctors = relationship("Doctor", back_populates="department")
    mappings = relationship("SymptomDepartmentMapping", back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    unavailable = relationship("DoctorUnavailable", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    patient_age = Column(Integer, nullable=False)
    patient_gender = Column(String, nullable=False)
    patient_email = Column(String, nullable=False)
    patient_phone = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    department_name = Column(String, nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    symptoms = Column(String, nullable=True)
    booking_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("Doctor", back_populates="appointments")

class DoctorUnavailable(Base):
    __tablename__ = "doctor_unavailable"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # For date ranges
    reason = Column(String, nullable=True)
    
    doctor = relationship("Doctor", back_populates="unavailable")

class SymptomDepartmentMapping(Base):
    __tablename__ = "symptom_department_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    symptom_keyword = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    default_severity = Column(String, nullable=True)
    
    department = relationship("Department", back_populates="mappings")
```

---

## AI Agent System

### 1. Symptom Analysis Agent

**Location:** `backend/app/agents/symptom_analysis.py`

**Purpose:** Analyzes patient symptoms and routes to appropriate department

**Components:**

#### a) Health Keyword Validation

```python
class SymptomAnalysisAgent:
    def __init__(self):
        self.health_keywords = [
            # General symptoms
            "pain", "ache", "fever", "cough", "cold",
            # Body parts
            "head", "chest", "stomach", "back", "knee",
            # Conditions
            "bleeding", "rash", "swelling", "anxiety",
            # Women's health
            "period", "pregnancy", "pelvic",
            # Mobility
            "walking", "mobility", "stiffness"
            # ... 70+ keywords total
        ]
    
    def _is_health_related(self, symptoms: str) -> bool:
        text = symptoms.lower()
        return any(k in text for k in self.health_keywords)
```

#### b) Severity Detection

```python
def _detect_severity(self, symptoms: str) -> str:
    text = symptoms.lower()
    
    # HIGH SEVERITY
    high_keywords = [
        "bleeding", "blood", "chest pain", "heart attack",
        "shortness of breath", "unconscious", "seizure",
        "severe", "unbearable", "fracture", "stroke"
    ]
    
    # LOW SEVERITY
    low_keywords = [
        "mild", "slight", "minor", "common cold",
        "runny nose", "dandruff", "bruise"
    ]
    
    if any(k in text for k in high_keywords):
        return "High"
    elif any(k in text for k in low_keywords):
        return "Low"
    else:
        return "Medium"
```

#### c) LLM Integration

```python
def analyze(self, db: Session, symptoms: str) -> SymptomAnalysisResult:
    # Step 1: Validate health-related
    if not self._is_health_related(symptoms):
        return SymptomAnalysisResult(
            False, None, None, 
            "Please mention health related symptoms"
        )
    
    # Step 2: Get available departments from DB
    available_depts = db.query(Department).all()
    dept_names = [dept.name for dept in available_depts]
    
    # Step 3: PRIMARY - Use LLM
    llm_result = self.llm_client.interpret_symptoms(
        symptoms, 
        available_departments=dept_names
    )
    
    if llm_result:
        dept = db.query(Department).filter(
            Department.name.ilike(f"%{llm_result}%")
        ).first()
        if dept:
            severity = self._detect_severity(symptoms)
            return SymptomAnalysisResult(
                True, dept.name, severity, None
            )
    
    # Step 4: FALLBACK - Rule-based mapping
    mapping_rows = db.query(SymptomDepartmentMapping).all()
    for row in mapping_rows:
        if row.symptom_keyword.lower() in symptoms.lower():
            severity = self._detect_severity(symptoms)
            return SymptomAnalysisResult(
                True, row.department.name, severity, None
            )
    
    # Step 5: LAST RESORT - General Medicine
    general_med = db.query(Department).filter(
        Department.name.ilike("%General Medicine%")
    ).first()
    
    if general_med:
        return SymptomAnalysisResult(
            True, general_med.name, "Medium",
            "⚠️ Referred to General Medicine for assessment"
        )
```

#### d) LLM Client (Groq Integration)

**Location:** `backend/app/agents/llm_client.py`

```python
class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-70b-versatile"
    
    def interpret_symptoms(
        self, 
        symptoms: str, 
        available_departments: List[str]
    ) -> Optional[str]:
        
        prompt = f"""You are a medical triage assistant. 
        
Patient symptoms: "{symptoms}"

Available departments in our hospital:
{', '.join(available_departments)}

Based on the symptoms, which department should the patient visit?

Rules:
1. Respond with ONLY the department name (exact match from list)
2. If multiple departments match, choose the most appropriate
3. If no specific match, respond with "General Medicine"
4. Do not explain, just give the department name

Department:"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 50
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                department = result["choices"][0]["message"]["content"].strip()
                return department
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
```

### 2. Scheduling Agent

**Location:** `backend/app/agents/scheduling_agent.py`

**Purpose:** Manages appointment slots and doctor availability

#### a) Slot Generation

```python
class SchedulingAgent:
    def _generate_daily_slots(self, day: date) -> List[datetime]:
        """Generate 30-min slots from 9 AM to 5 PM"""
        slots = []
        start_hour = 9   # 9 AM
        end_hour = 17    # 5 PM
        slot_duration = 30  # minutes
        
        current = datetime.combine(day, time(start_hour, 0))
        end = datetime.combine(day, time(end_hour, 0))
        
        while current < end:
            slots.append(current)
            current += timedelta(minutes=slot_duration)
        
        return slots
```

#### b) Leave Checking with Date Range Support

```python
def _is_doctor_unavailable(
    self, 
    db: Session, 
    doctor_id: int, 
    day: date
) -> bool:
    """
    Check if doctor is unavailable on given day.
    Supports both single-day and date range leaves.
    """
    leave_records = (
        db.query(DoctorUnavailable)
        .filter(DoctorUnavailable.doctor_id == doctor_id)
        .all()
    )
    
    for record in leave_records:
        # Date range leave
        if record.end_date:
            if record.date <= day <= record.end_date:
                return True
        # Single-day leave (backward compatible)
        else:
            if record.date == day:
                return True
    
    return False
```

#### c) Available Slots Retrieval

```python
def get_available_slots(
    self, 
    db: Session, 
    doctor_id: int, 
    days_ahead: int = 14
) -> List[datetime]:
    """Get all available slots for a doctor"""
    available = []
    now = datetime.now()
    today = now.date()
    
    for delta in range(days_ahead):
        target_date = today + timedelta(days=delta)
        
        # Skip if doctor is on leave
        if self._is_doctor_unavailable(db, doctor_id, target_date):
            continue
        
        # Generate slots for this day
        daily_slots = self._generate_daily_slots(target_date)
        
        for slot in daily_slots:
            # Skip past times
            if slot <= now:
                continue
            
            # Check if slot is already booked
            if not self._is_slot_taken(db, doctor_id, slot):
                available.append(slot)
    
    return available
```

#### d) Booking Validation

```python
def _is_slot_taken(
    self, 
    db: Session, 
    doctor_id: int, 
    slot: datetime
) -> bool:
    """Check if appointment slot is already booked"""
    existing = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_time == slot
        )
        .first()
    )
    return existing is not None
```

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────────┐
│   departments   │
├─────────────────┤
│ id (PK)         │
│ name (UNIQUE)   │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│     doctors     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ department_id(FK)│
│ email           │
│ is_active       │
└────┬────┬───────┘
     │    │
     │    │ 1:N
     │    │
     │    ├──────────────────────────┐
     │    │                          │
     │ 1:N│                          │
     │    │                          │
┌────▼────▼───────┐         ┌────────▼──────────────┐
│  appointments   │         │ doctor_unavailable    │
├─────────────────┤         ├───────────────────────┤
│ id (PK)         │         │ id (PK)               │
│ patient_name    │         │ doctor_id (FK)        │
│ patient_age     │         │ date                  │
│ patient_gender  │         │ end_date (NULLABLE)   │
│ patient_email   │         │ reason                │
│ patient_phone   │         └───────────────────────┘
│ doctor_id (FK)  │
│ department_name │
│ appointment_time│
│ symptoms        │
│ booking_id(UNIQ)│
│ created_at      │
└─────────────────┘

┌─────────────────┐
│   departments   │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼──────────────────┐
│symptom_department_mapping │
├───────────────────────────┤
│ id (PK)                   │
│ symptom_keyword           │
│ department_id (FK)        │
│ default_severity          │
└───────────────────────────┘
```

### Index Strategy

```sql
-- Primary Keys (Automatic indexes)
CREATE INDEX idx_departments_id ON departments(id);
CREATE INDEX idx_doctors_id ON doctors(id);
CREATE INDEX idx_appointments_id ON appointments(id);

-- Foreign Keys
CREATE INDEX idx_doctors_department_id ON doctors(department_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_unavailable_doctor_id ON doctor_unavailable(doctor_id);

-- Lookup Optimization
CREATE INDEX idx_appointments_booking_id ON appointments(booking_id);
CREATE INDEX idx_appointments_time ON appointments(appointment_time);
CREATE INDEX idx_unavailable_date ON doctor_unavailable(date);
CREATE INDEX idx_unavailable_end_date ON doctor_unavailable(end_date);

-- Composite Indexes
CREATE INDEX idx_appointments_doctor_time 
ON appointments(doctor_id, appointment_time);
```

---

## API Reference

### Patient APIs

#### 1. POST `/api/patient/triage`

**Description:** Analyze symptoms and get department recommendation

**Request Body:**
```json
{
  "symptoms": "I have severe chest pain and shortness of breath"
}
```

**Response (Success - 200):**
```json
{
  "is_valid": true,
  "department": "Cardiology",
  "severity": "High",
  "message": null,
  "doctors": [
    {
      "id": 2,
      "name": "Dr. Raj Patel",
      "email": "raj.patel@example.com"
    }
  ]
}
```

**Response (Invalid - 200):**
```json
{
  "is_valid": false,
  "department": null,
  "severity": null,
  "message": "Please mention health related symptoms",
  "doctors": []
}
```

#### 2. GET `/api/patient/doctors/{doctor_id}/available-slots`

**Description:** Get available appointment slots for specific doctor

**Path Parameters:**
- `doctor_id` (int): Doctor's ID

**Response (200):**
```json
{
  "doctor_id": 2,
  "doctor_name": "Dr. Raj Patel",
  "available_slots": [
    "2025-12-30T09:00:00",
    "2025-12-30T09:30:00",
    "2025-12-30T10:00:00",
    "2025-12-31T09:00:00"
  ]
}
```

**Response (404):**
```json
{
  "detail": "Doctor not found"
}
```

#### 3. POST `/api/patient/book`

**Description:** Book an appointment

**Request Body:**
```json
{
  "patient_name": "John Doe",
  "patient_age": 35,
  "patient_gender": "Male",
  "patient_email": "john@example.com",
  "patient_phone": "+91 9876543210",
  "doctor_id": 2,
  "appointment_time": "2025-12-30T10:00:00",
  "symptoms": "chest pain"
}
```

**Response (200):**
```json
{
  "id": 1,
  "patient_name": "John Doe",
  "doctor_name": "Dr. Raj Patel",
  "department_name": "Cardiology",
  "appointment_time": "2025-12-30T10:00:00",
  "booking_id": "ABC12345",
  "created_at": "2025-12-28T15:30:00"
}
```

**Response (400 - Slot Already Booked):**
```json
{
  "detail": "This time slot is already booked"
}
```

### Admin APIs

#### 1. POST `/api/admin/doctor-unavailable`

**Description:** Add doctor leave record

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Request Body:**
```json
{
  "doctor_id": 2,
  "date": "2025-12-27",
  "end_date": "2025-12-29",
  "reason": "Medical conference"
}
```

**Response (200):**
```json
{
  "id": 1,
  "doctor_id": 2,
  "doctor_name": "Dr. Raj Patel",
  "date": "2025-12-27",
  "end_date": "2025-12-29",
  "reason": "Medical conference"
}
```

**Response (400 - Invalid Date Range):**
```json
{
  "detail": "End date must be after or equal to start date"
}
```

#### 2. GET `/api/admin/doctor-unavailable`

**Description:** List all doctor leave records

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Response (200):**
```json
[
  {
    "id": 1,
    "doctor_id": 2,
    "doctor_name": "Dr. Raj Patel",
    "date": "2025-12-27",
    "end_date": "2025-12-29",
    "reason": "Medical conference"
  }
]
```

#### 3. GET `/api/admin/appointments`

**Description:** View all appointments

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Response (200):**
```json
[
  {
    "id": 1,
    "patient_name": "John Doe",
    "patient_age": 35,
    "patient_gender": "Male",
    "patient_email": "john@example.com",
    "patient_phone": "+91 9876543210",
    "doctor_id": 2,
    "doctor_name": "Dr. Raj Patel",
    "department_name": "Cardiology",
    "appointment_time": "2025-12-30T10:00:00",
    "symptoms": "chest pain",
    "booking_id": "ABC12345",
    "created_at": "2025-12-28T15:30:00"
  }
]
```

---

## Frontend Architecture

### Streamlit App Structure

**File:** `frontend/app.py`

#### 1. Configuration

```python
import streamlit as st
import requests
from datetime import datetime

API_BASE = "http://localhost:8002"

st.set_page_config(
    page_title="Get Life Hospital",
    page_icon="🏥",
    layout="wide"
)
```

#### 2. Custom CSS Styling

```python
st.markdown("""
<style>
    .main-header {
        font-size: 32px !important;
        color: white !important;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    /* ... more styles ... */
</style>
""", unsafe_allow_html=True)
```

#### 3. State Management

```python
# Initialize session state
if "triage_result" not in st.session_state:
    st.session_state.triage_result = None

if "selected_doctor_id" not in st.session_state:
    st.session_state.selected_doctor_id = None

if "available_slots" not in st.session_state:
    st.session_state.available_slots = []
```

#### 4. Component Structure

```
App Layout:
├── Header (Hospital Name + Logo)
├── Patient Section
│   ├── Medical Information
│   │   ├── Symptom Input (TextArea)
│   │   └── Analyze Button
│   ├── Triage Results Display
│   │   ├── Department Badge
│   │   ├── Severity Badge
│   │   └── Doctor List
│   └── Appointment Booking Form
│       ├── Patient Details
│       ├── Doctor Selection (triggers slot load)
│       ├── Date/Time Selection
│       └── Book Button
├── Admin Section
│   ├── Password Login
│   ├── View Appointments (with filters)
│   └── Doctor Leave Management
│       ├── Add Leave (with date range)
│       └── View Leaves
└── Footer
```

#### 5. Dynamic Slot Loading

```python
# Doctor selection callback
def on_doctor_change():
    doctor_id = st.session_state.get("selected_doctor_id")
    if doctor_id and doctor_id != "":
        with st.spinner("Loading available slots..."):
            try:
                response = requests.get(
                    f"{API_BASE}/api/patient/doctors/{doctor_id}/available-slots"
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.available_slots = data["available_slots"]
                else:
                    st.session_state.available_slots = []
                    st.error("Failed to load slots")
            except Exception as e:
                st.session_state.available_slots = []
                st.error(f"Error: {str(e)}")
    else:
        st.session_state.available_slots = []

# Doctor dropdown with callback
selected_doctor = st.selectbox(
    "Select Doctor",
    options=doctor_options,
    key="selected_doctor_id",
    on_change=on_doctor_change
)
```

---

## Configuration Management

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db

# AI/LLM Configuration
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
FROM_EMAIL=your_email@gmail.com

# Security
ADMIN_PASSWORD=your_secure_admin_password

# Hospital Information
HOSPITAL_NAME=Get Life Hospital
HOSPITAL_ADDRESS=123 Medical Street, Healthcare City
HOSPITAL_PHONE=+91 1234567890
HOSPITAL_EMAIL=info@getlifehospital.com
```

### Email Setup (Gmail App Password)

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate password for "Mail" application
5. Use this 16-character password in `.env`

---

## Deployment Guide

### Local Development

```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 2: Frontend
streamlit run frontend/app.py
```

### Production Deployment

#### Backend (Railway/Render)

**Procfile:**
```
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
Set all variables from `.env` in platform dashboard

**Database:**
Use managed PostgreSQL (Railway Postgres, ElephantSQL, etc.)

#### Frontend (Streamlit Cloud)

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set secrets in Streamlit dashboard (`.streamlit/secrets.toml` format)
4. Deploy from `version1` branch

**secrets.toml format:**
```toml
API_BASE = "https://your-backend.railway.app"
```

### Docker Deployment (Optional)

**Dockerfile (Backend):**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY .env .

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend ./frontend

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: hospital_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8002:8002"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://admin:password@postgres:5432/hospital_db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## Performance Optimization

### Database Queries

1. **Use Indexes:** All foreign keys and frequently queried fields are indexed
2. **Eager Loading:** Use `.join()` to prevent N+1 queries
3. **Connection Pooling:** SQLAlchemy manages connection pool automatically

### API Response Time

- **Target:** < 500ms for most endpoints
- **LLM Timeout:** 10 seconds
- **Caching:** Consider Redis for frequently accessed data

### Scaling Considerations

1. **Horizontal Scaling:** Stateless FastAPI allows multiple instances
2. **Database Replication:** Read replicas for appointment listings
3. **CDN:** Serve static assets via CDN
4. **Load Balancer:** Distribute traffic across backend instances

---

## Security Best Practices

### Implemented

✅ Admin password protection
✅ Input validation (Pydantic schemas)
✅ SQL injection prevention (SQLAlchemy ORM)
✅ CORS configuration
✅ Environment variable for secrets

### Recommended Additions

🔐 **Authentication:**
- JWT tokens for patient sessions
- OAuth integration (Google, Facebook)

🔐 **Authorization:**
- Role-based access control (RBAC)
- Doctor-specific endpoints

🔐 **Data Protection:**
- Encrypt sensitive data at rest
- HIPAA compliance measures
- Audit logs for all actions

🔐 **API Security:**
- Rate limiting (10 requests/minute)
- API key authentication
- Request validation middleware

---

## Testing Strategy

### Unit Tests

```python
# Example: Test symptom analysis
def test_symptom_analysis_chest_pain():
    agent = SymptomAnalysisAgent()
    result = agent.analyze(db, "severe chest pain")
    assert result.is_valid == True
    assert result.department == "Cardiology"
    assert result.severity == "High"
```

### Integration Tests

```python
# Example: Test booking flow
def test_booking_flow():
    # 1. Triage
    response = client.post("/api/patient/triage", 
        json={"symptoms": "fever"})
    assert response.status_code == 200
    
    # 2. Get slots
    response = client.get("/api/patient/doctors/1/available-slots")
    slots = response.json()["available_slots"]
    
    # 3. Book appointment
    response = client.post("/api/patient/book", json={
        "patient_name": "Test User",
        "doctor_id": 1,
        "appointment_time": slots[0]
    })
    assert response.status_code == 200
```

### Load Testing

Use tools like:
- **Locust** for API load testing
- **Apache JMeter** for stress testing
- **K6** for performance testing

---

## Monitoring & Logging

### Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Booking created: {booking_id}")
logger.error(f"LLM API failed: {str(e)}")
```

### Metrics to Track

- API response times
- LLM API success rate
- Booking conversion rate
- Error rates by endpoint
- Database query performance

### Tools

- **Sentry** - Error tracking
- **Grafana** - Metrics visualization
- **Prometheus** - Metrics collection
- **ELK Stack** - Log aggregation

---

## Troubleshooting Guide

### Common Issues

1. **"Doctor not found" error**
   - Run `python -m backend.app.seed_data` to seed database

2. **LLM not working**
   - Verify `GROQ_API_KEY` in `.env`
   - Check Groq API quota
   - System falls back to rules automatically

3. **Email not sending**
   - Use Gmail App Password (not regular password)
   - Enable "Less secure app access" (old method)
   - Check SMTP settings

4. **Slots not loading**
   - Ensure backend is running on port 8002
   - Check `API_BASE` in frontend matches backend URL
   - Verify doctor has no overlapping leaves

---

## Version Control

### Branch Strategy

- `main` - Production-ready code
- `version1` - Feature development
- `feature/*` - Individual features
- `hotfix/*` - Urgent fixes

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

---

## Glossary

- **Triage:** Process of determining patient priority/department
- **LLM:** Large Language Model (AI for text understanding)
- **ORM:** Object-Relational Mapping (SQLAlchemy)
- **ASGI:** Asynchronous Server Gateway Interface
- **SMTP:** Simple Mail Transfer Protocol
- **CORS:** Cross-Origin Resource Sharing

---

**Document Version:** 1.0
**Last Updated:** December 28, 2025
**Author:** Rohit Barde

