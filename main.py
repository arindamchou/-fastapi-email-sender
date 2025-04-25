from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.message import EmailMessage
import os

app = FastAPI()

# Model for incoming request
class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

# Load Gmail credentials from environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Use App Password if 2FA is on

@app.post("/send-email")
def send_email(request: EmailRequest):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="Email credentials not configured")

    msg = EmailMessage()
    msg["Subject"] = request.subject
    msg["From"] = GMAIL_USER
    msg["To"] = request.to
    msg.set_content(request.body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            smtp.send_message(msg)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
