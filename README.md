# 🏥 Get Life Hospital - AI-Powered Appointment System

## 📋 Project Overview

An intelligent multi-agent hospital appointment management system that uses AI (LLM) for symptom analysis and automatic department/doctor recommendations. The system streamlines patient triage, appointment scheduling, and administrative tasks.

## ✨ Key Features

### 🤖 AI-Powered Triage System
- **Symptom Analysis Agent**: Uses Groq LLM (Llama 3.1) to understand natural language symptom descriptions
- **Intelligent Department Routing**: Automatically routes patients to the appropriate medical department
- **Severity Detection**: Auto-detects urgency levels (High/Medium/Low) based on symptoms
- **Fallback System**: Rule-based mapping as backup when LLM is unavailable

### 📅 Smart Appointment Scheduling
- **Dynamic Slot Generation**: Automatically generates available time slots (9 AM - 5 PM)
- **Doctor Leave Management**: Supports single-day and date-range leave periods
- **Real-time Availability**: Shows only available dates for selected doctors
- **Conflict Prevention**: Prevents double-booking of appointments

### 👨‍⚕️ Doctor Management
- Multiple specialties support
- Dynamic doctor-wise appointment filtering
- Email notifications for appointments
- Department-based organization

### 🔐 Admin Dashboard
- **Doctor Leave Management**: Add/view doctor unavailability with date ranges
- **Appointment Overview**: View all bookings with filters (date, doctor, department)
- **Department Management**: Manage departments and doctors
- **Secure Access**: Password-protected admin interface

### 📧 Email Notifications
- Professional appointment confirmation emails
- Booking ID generation for reference
- Detailed appointment information
- SMTP integration with Gmail

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **AI/LLM**: Groq API (Llama 3.1 70B)
- **Email**: SMTP (Gmail)
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: Streamlit
- **UI Components**: Custom CSS styling
- **API Integration**: Python requests library

### Database Schema
- **Departments**: Medical specialties
- **Doctors**: Healthcare providers with department associations
- **Appointments**: Booking records with patient details
- **Doctor Unavailable**: Leave management with date ranges
- **Symptom Department Mapping**: Rule-based symptom routing

## 📁 Project Structure

```
Hospital Appointment System/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── llm_client.py          # Groq LLM integration
│   │   │   ├── symptom_analysis.py    # AI symptom analyzer
│   │   │   └── scheduling_agent.py    # Appointment scheduling logic
│   │   ├── routers/
│   │   │   ├── admin.py               # Admin endpoints
│   │   │   └── patient.py             # Patient endpoints
│   │   ├── models.py                  # Database models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   ├── database.py                # DB connection
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── seed_data.py               # Database seeding
│   │   └── migrate_add_end_date.py    # Migration script
│   └── requirements.txt
├── frontend/
│   ├── app.py                         # Streamlit UI
│   └── requirements.txt
├── .env                               # Environment variables
└── README.md

```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL database
- Groq API key (free at https://groq.com)
- Gmail account for email notifications

### 1. Clone Repository
```bash
git clone https://github.com/rohitmbarde/Hospital-Appointment-System.git
cd Hospital-Appointment-System
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

**Backend:**
```bash
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
pip install -r frontend/requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in root directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db

# Groq AI
GROQ_API_KEY=your_groq_api_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com

# Admin Access
ADMIN_PASSWORD=your_secure_password

# Hospital Details
HOSPITAL_NAME=Get Life Hospital
HOSPITAL_ADDRESS=123 Medical Street, Healthcare City, HC 12345
HOSPITAL_PHONE=+91 1234567890
HOSPITAL_EMAIL=info@getlifehospital.com
```

### 5. Initialize Database

```bash
# Create database tables and seed initial data
python -m backend.app.seed_data
```

### 6. Run Migration (for date range feature)

```bash
# Add end_date column for leave management
python backend/app/migrate_add_end_date.py
```

### 7. Start Backend Server

```bash
cd "path/to/Hospital Appointment system"
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 0.0.0.0 --port 8002 --reload
```

Backend runs on: **http://localhost:8002**

### 8. Start Frontend

Open a new terminal:

```bash
cd "path/to/Hospital Appointment system"
streamlit run frontend/app.py
```

Frontend runs on: **http://localhost:8501**

## 📖 User Guide

### For Patients

1. **Describe Symptoms**
   - Enter your symptoms in natural language
   - Example: "I have severe chest pain and difficulty breathing"

2. **View Triage Results**
   - System analyzes symptoms using AI
   - Shows recommended department and severity level

3. **Select Doctor**
   - Choose from available doctors in recommended department
   - System shows only that doctor's available slots

4. **Book Appointment**
   - Fill in personal details (name, age, gender, contact)
   - Select available date/time slot
   - Confirm booking

5. **Get Confirmation**
   - Receive booking ID for reference
   - Email confirmation sent to registered email

### For Admins

1. **Login**
   - Enter admin password from `.env` file

2. **View Appointments**
   - See all bookings in table format
   - Filter by date, doctor, or department

3. **Manage Doctor Leaves**
   - Add single-day or date-range leaves
   - View all leave records
   - System automatically blocks slots during leave periods

## 🔌 API Endpoints

### Patient APIs

**POST** `/api/patient/triage`
- Analyze symptoms and get department recommendation
- Request body: `{ "symptoms": "headache and dizziness" }`

**GET** `/api/patient/doctors/{doctor_id}/available-slots`
- Get available slots for specific doctor
- Respects doctor leave periods

**POST** `/api/patient/book`
- Book an appointment
- Sends email confirmation

### Admin APIs

**POST** `/api/admin/doctor-unavailable`
- Add doctor leave record
- Supports date ranges (start_date + end_date)

**GET** `/api/admin/doctor-unavailable`
- List all doctor leaves

**GET** `/api/admin/appointments`
- View all appointments

## 🧪 Sample Test Cases

### Symptom Analysis Test Cases

| Symptom Input | Expected Department | Severity |
|---------------|-------------------|----------|
| "severe chest pain" | Cardiology | High |
| "difficulty swallowing" | ENT | Medium |
| "irregular periods" | General Medicine | Medium |
| "kidney pain" | General Medicine | Medium |
| "difficulty walking" | Orthopedics | Medium |
| "fever and cough" | General Medicine | Medium |
| "anxiety and stress" | Psychiatry | Medium |

## 🔒 Security Features

- Admin password protection
- Input validation on all forms
- SQL injection prevention (SQLAlchemy ORM)
- Email validation
- Secure SMTP with TLS

## 🌟 Unique Features

1. **Date Range Leave Management**: Admins can set leave periods instead of marking individual days
2. **Dynamic Slot Filtering**: Slots update in real-time based on doctor selection
3. **AI + Rule Hybrid**: Falls back to rules when LLM is unavailable
4. **Professional Email Templates**: Branded appointment confirmations
5. **Backward Compatibility**: Supports both old (single-day) and new (date-range) leave records

## 📊 Database Schema

### Tables

**departments**
- id, name

**doctors**
- id, name, department_id, email, is_active

**appointments**
- id, patient_name, patient_age, patient_gender, patient_email, patient_phone
- doctor_id, department_name, appointment_time, symptoms, booking_id, created_at

**doctor_unavailable**
- id, doctor_id, date, end_date, reason

**symptom_department_mapping**
- id, symptom_keyword, department_id, default_severity

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check if port 8002 is already in use
netstat -ano | findstr :8002

# Kill the process if needed
taskkill /PID <process_id> /F
```

### Frontend Connection Error
- Ensure backend is running on port 8002
- Check `API_BASE` in `frontend/app.py` matches backend port

### Email Not Sending
- Enable "Less secure app access" or use App Password for Gmail
- Verify SMTP credentials in `.env`

### Database Connection Error
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

## 🚢 Deployment

### Backend (Railway/Render/DigitalOcean)
1. Set environment variables
2. Install dependencies
3. Run migrations
4. Start with: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Streamlit Cloud)
1. Connect GitHub repository
2. Set secrets in Streamlit dashboard
3. Deploy from branch

## 📝 Version History

### Version 1 (Current Branch: `version1`)
- ✅ AI-powered symptom analysis
- ✅ Dynamic appointment scheduling
- ✅ Date range leave management
- ✅ Doctor-wise slot filtering
- ✅ Email notifications
- ✅ Professional UI with healthcare theme
- ✅ Admin dashboard with filtering

## 👥 Contributors

- **Rohit Barde** - Developer
- Repository: https://github.com/rohitmbarde/Hospital-Appointment-System

## 📄 License

This project is for educational/demonstration purposes.

## 🤝 Support

For issues or questions:
- Create an issue on GitHub
- Email: rohitmbarde@example.com

---

**Built with ❤️ for Get Life Hospital**
