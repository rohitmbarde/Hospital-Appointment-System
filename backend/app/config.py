import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, AnyHttpUrl, EmailStr

# Load environment variables from a .env file at project root if present.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)


class Settings(BaseModel):
    app_name: str = "Hospital Appointment & Routing Assistant"
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://localhost/hospital"))
    hospital_start_hour: int = Field(default_factory=lambda: int(os.getenv("HOSPITAL_START_HOUR", "9")))
    hospital_end_hour: int = Field(default_factory=lambda: int(os.getenv("HOSPITAL_END_HOUR", "17")))
    lunch_start_hour: int = 13
    lunch_end_hour: int = 14
    admin_password: str = Field(default_factory=lambda: os.getenv("ADMIN_PASSWORD", "Admin123"))
    email_sender: EmailStr | None = Field(default_factory=lambda: os.getenv("EMAIL_SENDER"))
    email_sender_password: str | None = Field(default_factory=lambda: os.getenv("EMAIL_SENDER_PASSWORD"))
    email_smtp_server: str = Field(default_factory=lambda: os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"))
    email_smtp_port: int = Field(default_factory=lambda: int(os.getenv("EMAIL_SMTP_PORT", "587")))
    groq_api_key: str | None = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    groq_model: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))


def get_settings() -> Settings:
    return Settings()

