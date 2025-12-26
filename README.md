# Hospital Appointment & Routing Assistant

Multi-agent system for hospital appointment booking with symptom analysis, department routing, and scheduling.

## Tech Stack
- **Backend**: FastAPI + Python 3.12
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI/LLM**: Groq (llama-3.1-8b-instant) for ambiguous symptom interpretation
- **Agents**: 
  - Symptom Analysis Agent (rule-based + LLM fallback)
  - Specialist Recommendation Agent (enforces pediatrics <13, checks availability)
  - Scheduling Agent (excludes lunch 1-2 PM, doctor leave days)

## Prerequisites
- Python 3.12 (recommended; 3.11 also works)
- PostgreSQL running locally or remotely
- Groq API key (optional, for LLM fallback)

## Setup

### 1. Install Dependencies
```bash
# Create virtual environment
py -3.12 -m venv .venv

# Activate (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Install packages
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file at project root (copy from `env.example`):

```env
DATABASE_URL=postgresql://postgres:Admin%40123@localhost:5432/hospital_db
ADMIN_PASSWORD=Admin123
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Optional: Email confirmation (leave blank to skip email sending)
# For Gmail: Use App Password, not regular password
# https://support.google.com/accounts/answer/185833
EMAIL_SENDER=your_email@gmail.com
EMAIL_SENDER_PASSWORD=your_app_password_here
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

HOSPITAL_START_HOUR=9
HOSPITAL_END_HOUR=17
```

**Note**: For passwords with special characters (like `@`), use URL encoding (`%40` for `@`).

### 3. Create Database
```sql
CREATE USER postgres WITH PASSWORD 'Admin@123';
CREATE DATABASE hospital_db OWNER postgres;
```

### 4. Run Migration (Add end_date column)
```bash
python -m backend.app.migrate_add_end_date
```

### 5. Seed Data
```bash
python -m backend.app.seed_data
```
This populates:
- 8 departments (General Medicine, Cardiology, Neurology, Pediatrics, Orthopedics, Dermatology, ENT, Psychiatry)
- Sample doctors per department
- Symptom-to-department mappings

## Running the Application

### Start Backend API (Terminal 1)
```bash
# In project root, with venv activated
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\uvicorn.exe backend.app.main:app --reload --port 8002
```
API will be available at: http://127.0.0.1:8002
- Docs: http://127.0.0.1:8002/docs

### Start Frontend (Terminal 2)
```bash
# In project root, with venv activated
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
$env:API_BASE_URL="http://localhost:8002"
streamlit run frontend/app.py
```
Streamlit UI will open at: http://localhost:8501

## Usage

### Patient Flow
1. Select **Patient** role
2. Enter:
   - Name, Age, Gender, Email
   - Symptoms (e.g., "chest pain and shortness of breath")
3. Click **Analyze & Show Slots**
4. System returns:
   - Identified department
   - Severity level (Low/Medium/High)
   - Recommended doctor(s)
   - Available appointment slots (excludes lunch 1-2 PM and doctor leave)
5. Select doctor and slot, click **Confirm Booking**
6. Appointment confirmed (email sent if SMTP configured)

### Admin Flow
1. Select **Admin** role
2. Enter admin password (default: `Admin123`)
3. **Appointments Management**:
   - View all appointments in professional table format
   - Filter by Doctor, Department, or Date
   - View statistics (total, high severity, emails sent, unique patients)
4. **Doctor Leave Management**:
   - View all doctor leave records with date ranges
   - Add new leave records:
     - Select doctor from dropdown
     - Choose leave start date
     - Optionally choose leave end date for multi-day leave
     - Provide reason
   - See total leave days statistics
5. View patient records (via API)

## Key Features
✅ Rule-based symptom → department mapping (primary)  
✅ LLM fallback for vague symptoms (e.g., "feeling uneasy and low")  
✅ Pediatrics routing only for patients <13 years  
✅ Lunch hour exclusion (1-2 PM)  
✅ Doctor leave day exclusion  
✅ Email confirmation (fail-safe: booking succeeds even if email fails)  
✅ Admin dashboard for appointment/leave management  

## Troubleshooting

### "No module named 'fastapi_mail'"
Make sure you're running uvicorn from the venv:
```bash
.\.venv\Scripts\uvicorn.exe backend.app.main:app --reload --port 8002
```

### "Mapped department not found"
Re-run seed script to ensure departments exist:
```bash
python -m backend.app.seed_data
```

### Email sending fails
- If SMTP creds are not set (`EMAIL_SENDER` blank), email step is skipped silently
- If creds are wrong, booking still succeeds (fail-safe mode)

### Python 3.13 build errors
Use Python 3.12 or 3.11 (prebuilt wheels available):
```bash
py -3.12 -m venv .venv
```

## Testing
```bash
pytest tests/test_scheduling.py
```

## Project Structure
```
Hospital Appointment system/
├── backend/
│   └── app/
│       ├── agents/           # Multi-agent modules
│       │   ├── llm_client.py
│       │   ├── symptom_analysis.py
│       │   ├── specialist_recommendation.py
│       │   └── scheduling_agent.py
│       ├── routers/          # API endpoints
│       │   ├── patient.py
│       │   └── admin.py
│       ├── services/         # Email service
│       ├── config.py         # Settings & env loading
│       ├── database.py       # SQLAlchemy setup
│       ├── models.py         # DB models
│       ├── schemas.py        # Pydantic schemas
│       ├── seed_data.py      # Database seeder
│       └── main.py           # FastAPI app
├── frontend/
│   └── app.py                # Streamlit UI
├── tests/
│   └── test_scheduling.py    # Scheduling tests
├── .env                      # Environment config (not in git)
├── env.example               # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Schema
- `patients`: Patient records
- `departments`: Hospital departments
- `doctors`: Doctor profiles (linked to departments)
- `doctor_unavailable`: Leave/unavailability dates
- `appointments`: Booked appointments
- `symptom_department_mapping`: Symptom → department routing table

## License
Educational project for hospital appointment management.

