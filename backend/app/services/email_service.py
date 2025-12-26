from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import get_settings


class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self._fastmail: Optional[FastMail] = None
        if self.settings.email_sender and self.settings.email_sender_password:
            self._fastmail = FastMail(
                ConnectionConfig(
                    MAIL_USERNAME=self.settings.email_sender,
                    MAIL_PASSWORD=self.settings.email_sender_password,
                    MAIL_FROM=self.settings.email_sender,
                    MAIL_PORT=self.settings.email_smtp_port,
                    MAIL_SERVER=self.settings.email_smtp_server,
                    MAIL_STARTTLS=True,
                    MAIL_SSL_TLS=False,
                    USE_CREDENTIALS=True,
                )
            )

    async def send_confirmation(
        self,
        to_email: str,
        patient_name: str,
        doctor_name: str,
        department_name: str,
        appointment_dt: str,
        booking_id: int = None,
    ) -> bool:
        """
        Send confirmation email. Returns True if sent successfully, False otherwise.
        Never raises exceptions (fail-safe for booking flow).
        """
        if not self._fastmail:
            # Email disabled; skip quietly
            return False
        
        # Parse appointment datetime
        from datetime import datetime
        try:
            dt_obj = datetime.fromisoformat(appointment_dt)
            date_str = dt_obj.strftime("%Y-%m-%d")
            time_str = dt_obj.strftime("%H:%M")
        except:
            date_str = appointment_dt
            time_str = "TBD"
        
        # Generate booking reference ID in hex format
        booking_ref = f"{booking_id:08X}" if booking_id else "N/A"
        
        body = f"""✅ Appointment Confirmed
Hospital Appointment System

Dear {patient_name},

Thank you for connecting with Hospital Appointment System.

Your appointment has been successfully scheduled. Below are the details of your appointment for your reference:

📋 Appointment ID: {booking_ref}

📅 Date: {date_str}

⏰ Time: {time_str}

👨‍⚕️ Doctor: Dr. {doctor_name}

🏥 Department: {department_name}

📝 Special Note:

Please bring your insurance card and valid ID to your appointment.

📌 Important Instructions
Please arrive 10-15 minutes before your appointment time
Bring a valid ID and any relevant medical documents
If you have any medical allergies, please inform the staff
If you need to cancel or reschedule, contact us at least 24 hours in advance

For any queries, please contact the hospital reception.

Thank you for choosing our services!

Best regards,
Hospital Appointment Team
"""
        
        message = MessageSchema(
            subject="✅ Appointment Confirmed - Hospital Appointment System",
            recipients=[to_email],
            body=body,
            subtype="plain",
        )
        try:
            await self._fastmail.send_message(message)
            return True
        except Exception:
            # Fail-safe: do not block booking if email fails
            return False

