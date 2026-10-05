import pytest
from fastapi.testclient import TestClient
from app.main import app, seed_database
from app.services.category_classifier import classify_category, CategoryClassifierService

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed_database()
    yield

client = TestClient(app)

def test_category_classifier_fallback_or_prediction():
    """Test that classify_category returns valid dict with category and confidence."""
    result = classify_category("URGENT: Verify your bank account login credentials immediately.")
    assert "category" in result
    assert "confidence" in result
    assert isinstance(result["category"], str)
    assert isinstance(result["confidence"], float)

def test_analyze_email_endpoint_category_fields():
    """Test that email analysis returns phishing_category and category_confidence fields."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/emails/analyze", json={
        "sender": "security@bank-alert.com",
        "subject": "Action Required: Bank Account Suspended",
        "body": "Your bank account has been suspended. Please click http://bank-verify.com to restore access."
    }, headers=headers)
    assert res.status_code == 200
    payload = res.json()
    assert "phishing_category" in payload
    assert "category_confidence" in payload
    assert payload["phishing_category"] is not None

def test_email_history_endpoint_category_fields():
    """Test that history endpoint includes category information for every item."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/emails/history", headers=headers)
    assert res.status_code == 200
    history = res.json()
    assert len(history) > 0
    item = history[0]
    assert "phishing_category" in item
    assert "category_confidence" in item

def test_dashboard_category_distribution():
    """Test that dashboard analytics payload includes category_distribution."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "category_distribution" in data
    assert isinstance(data["category_distribution"], list)
