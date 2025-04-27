from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.message import EmailMessage
import os
from io import BytesIO
from fpdf import FPDF  # pip install fpdf

app = FastAPI()


# Model for incoming request
class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


# Load Gmail credentials from environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Use App Password if 2FA is on


def convert_body_to_pdf(body: str) -> bytes:
    """
    Convert the email body into a PDF and return as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Add body content (handling multi-line)
    for line in body.splitlines():
        pdf.multi_cell(0, 10, line)

    # Save PDF to a BytesIO object
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.read()


@app.post("/send-email")
def send_email(request: EmailRequest):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="Email credentials not configured")

    msg = EmailMessage()
    msg["Subject"] = request.subject
    msg["From"] = GMAIL_USER
    msg["To"] = request.to
    msg.set_content("Please find the attached PDF document.")  # Set a simple text

    try:
        # Convert body to PDF
        pdf_data = convert_body_to_pdf(request.body)

        # Attach the PDF
        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename="email_body.pdf"
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            smtp.send_message(msg)
        return {"message": "Email with PDF attachment sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
