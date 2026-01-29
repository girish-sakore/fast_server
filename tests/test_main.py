import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
# Mock environment variables before importing the app for setting env variables
os.environ["GMAIL_SENDER_EMAIL"] = "mock_sender@gmail.com"
os.environ["GMAIL_RECIEVER_EMAIL"] = "mock_receiver@gmail.com"

from main import app

client = TestClient(app)

# Test the root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "sender": "mock_sender@gmail.com",
        "reciever": "mock_receiver@gmail.com",
        "message": "Fast API is running.",
    }

# Test the /track-qr-visit endpoint
@pytest.mark.asyncio
@patch("main.database.execute", new_callable=AsyncMock)
async def test_track_qr_visit(mock_execute):
    mock_execute.return_value = None  # Mock successful database insertion
    data = {
        "source": "test_source",
        "timestamp": "2023-01-01T00:00:00Z",
        "userAgent": "test_user_agent",
        "pagePath": "/test/path",
    }
    response = client.post("/track-qr-visit", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "QR visit tracked successfully!"}

# Test the /submit-contact/ endpoint
@pytest.mark.asyncio
@patch("main.send_contact_email")
async def test_submit_contact_form(mock_send_contact_email):
    mock_send_contact_email.return_value = {"message": "Email sent successfully!"}
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Subject",
        "message": "Test Message",
    }
    response = client.post("/submit-contact/", json=form_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Email sent successfully!"}