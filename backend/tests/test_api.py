import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app, seed_database
from app.database import Base, engine, SessionLocal
from app.models import User

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed_database()
    yield

client = TestClient(app)

def test_authentication_flow():
    unique_email = f"officer_{uuid.uuid4().hex[:6]}@security.com"
    
    # Register new user
    reg_response = client.post("/api/auth/register", json={
        "name": "Test Security Officer",
        "email": unique_email,
        "password": "SecurePassword123!"
    })
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    token = data["access_token"]

    # Login user
    login_response = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "SecurePassword123!"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    # Get current user profile
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == unique_email

def test_email_analysis_endpoint():
    # Login as seeded admin user
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    assert login_res.status_code == 200
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Test phishing email analysis
    res = client.post("/api/emails/analyze", json={
        "sender": "security-alert@paypal-update.com",
        "subject": "Urgent: Verify your PayPal account immediately",
        "body": "Dear customer, click http://192.168.1.1/login to verify your account or it will be suspended."
    }, headers=headers)
    assert res.status_code == 200
    payload = res.json()
    assert payload["is_phishing"] is True
    assert payload["risk_level"] in ["HIGH", "CRITICAL"]

def test_future_risk_prediction_endpoint():
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/prediction/future-risk", headers=headers)
    assert res.status_code == 200
    payload = res.json()
    assert "future_risk_probability" in payload
    assert "predicted_risk" in payload
    assert "features_used" in payload

def test_analytics_dashboard_endpoint():
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    payload = res.json()
    assert "stats" in payload
    assert "daily_trend" in payload
    assert "phishing_vs_legit" in payload
