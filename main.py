from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from email_service import send_contact_email
from config import GMAIL_SENDER_EMAIL, GMAIL_RECIEVER_EMAIL
from datetime import datetime, timezone
from database import database, qr_visits

app = FastAPI()

origins = [
    "https://proximacloud.in",
    "https://www.proximacloud.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- Pydantic Model for Incoming QR Visit Data ---
class QRVisit(BaseModel):
    source: str
    timestamp: datetime
    userAgent: str
    pagePath: str

# --- FastAPI Endpoint to track QR visits ---
@app.post("/track-qr-visit")
async def track_qr_visit(data: QRVisit):
    """
    Tracks a QR visit and stores the data in the PostgreSQL database.
    """

    query = qr_visits.insert().values(
        source=data.source,
        timestamp=data.timestamp,
        useragent=data.userAgent,
        pagepath=data.pagePath,
    )
    try:
        await database.execute(query)
        return {"message": "QR visit tracked successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track QR visit: {str(e)}")

# --- Pydantic Model for Incoming Form Data ---
class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str

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
        "message": "Fast API is running."
    }