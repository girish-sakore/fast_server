import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://proximacloud.ddns.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GMAIL_RECIEVER_EMAIL = os.getenv("GMAIL_RECIEVER_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port

# --- Pydantic Model for Incoming Form Data ---
class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str

# --- Email Sending Logic ---
def send_contact_email(form_data: ContactForm):
    """
    Sends an email containing the contact form data to the GMAIL_SENDER_EMAIL.
    """
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_SENDER_EMAIL
        msg['To'] = GMAIL_RECIEVER_EMAIL
        msg['Subject'] = Header(f"New Contact Form Submission: {form_data.subject}", 'utf-8').encode()

        # Construct the email body with the form data
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #0056b3;">New Contact Form Submission</h2>
                <p>You have received a new message from your contact form:</p>
                <hr style="border-top: 1px solid #eee;">
                <p><strong>Name:</strong> {form_data.name}</p>
                <p><strong>Email:</strong> {form_data.email}</p>
                <p><strong>Subject:</strong> {form_data.subject}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 3px solid #007bff; margin-top: 10px; border-radius: 4px;">
                    <p style="white-space: pre-wrap;">{form_data.message}</p>
                </div>
                <hr style="border-top: 1px solid #eee; margin-top: 20px;">
                <p style="font-size: 0.9em; color: #777;">This email was sent from your website's contact form.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(email_body, 'html', 'utf-8'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"Contact form email sent successfully from {form_data.email} to {GMAIL_SENDER_EMAIL}")
        return {"message": "Contact form submitted successfully!"}

    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="SMTP Authentication Error. Check your GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD."
        )
    except smtplib.SMTPConnectError:
        raise HTTPException(
            status_code=500,
            detail="SMTP Connection Error. Could not connect to Gmail's SMTP server. Check internet connection or firewall."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while sending email: {str(e)}"
        )

# --- FastAPI Endpoint to receive form data ---
@app.post("/submit-contact/")
async def submit_contact_form(form_data: ContactForm):
    """
    Receives contact form data and sends it as an email to the configured Gmail account.
    """
    try:
        result = send_contact_email(form_data)
        return result
    except HTTPException as e:
        # Re-raise HTTPExceptions caught from send_contact_email
        raise e
    except Exception as e:
        # Catch any other unexpected errors and return a 500
        raise HTTPException(status_code=500, detail=f"Failed to process contact form: {str(e)}")

# --- Root endpoint for health check ---
@app.get("/")
async def root():
    return {
        "sender": GMAIL_SENDER_EMAIL,
        "reciever": GMAIL_RECIEVER_EMAIL,
        "message": "Contact form API is running. Use /submit-contact/ to send form data."
        }