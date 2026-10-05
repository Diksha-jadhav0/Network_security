import os
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models import User, Email
from .routes import auth, emails, analytics, prediction
from .routes.auth import get_password_hash
from .services.phishing_detector import PhishingDetectorService
from .services.risk_predictor import RiskPredictorService

app = FastAPI(
    title="Phishing Email Risk Prediction API",
    description="Network Security & Machine Learning API for email threat detection and future phishing risk score analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows requests from React frontend (http://localhost:3000, http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(analytics.router)
app.include_router(prediction.router)

from sqlalchemy import inspect, text

def seed_database():
    """Create tables, ensure demo user exists, and populate initial emails for dashboard."""
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Schema migration check for SQLite
        try:
            inspector = inspect(engine)
            if "emails" in inspector.get_table_names():
                cols = [c["name"] for c in inspector.get_columns("emails")]
                if "phishing_category" not in cols:
                    db.execute(text("ALTER TABLE emails ADD COLUMN phishing_category VARCHAR"))
                if "category_confidence" not in cols:
                    db.execute(text("ALTER TABLE emails ADD COLUMN category_confidence FLOAT DEFAULT 0.0"))
                db.commit()
        except Exception as e:
            print(f"Migration check notice: {e}")

        # 1. Create Demo User: admin@example.com / Admin@123
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            print("Creating default demo user: admin@example.com / Admin@123")
            admin_user = User(
                name="Security Administrator",
                email="admin@example.com",
                password_hash=get_password_hash("Admin@123")
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        # 2. Check if emails exist, if not insert 25 realistic sample emails
        email_count = db.query(Email).filter(Email.user_id == admin_user.id).count()
        if email_count == 0:
            print("Seeding database with 25 initial email samples for analytics...")
            sample_emails = [
                # Phishing emails with categories
                ("security-update@paypa1-alert.com", "Verify your PayPal account immediately", "Dear customer, unauthorized login detected. Click http://paypa1-security.com/login to restore access.", True, 0.94, "HIGH", "ACCOUNT_VERIFICATION_SCAM", 0.95, 1, ["verify", "unauthorized"]),
                ("hr-update@company-payroll-portal.info", "Action Required: Salary Deposit Failed", "Please update your bank routing details at http://hr-direct-deposit.tech/payroll to receive monthly salary.", True, 0.92, "HIGH", "TRANSACTION_FRAUD", 0.91, 1, ["action required", "deposit", "failed"]),
                ("it-help@office365-password-reset.com", "Office 365 Password Expiration Alert", "Your password expires in 2 hours. Confirm credentials at http://microsoft-sso-verify.net/sso.", True, 0.89, "HIGH", "ACCOUNT_VERIFICATION_SCAM", 0.93, 1, ["password", "expiration"]),
                ("tax-claim@irs-government-tax-refund.top", "IRS Tax Refund of $1,420 Approved", "Submit your social security number and card details at http://192.168.1.105/irs/claim.", True, 0.97, "CRITICAL", "BANKING_FRAUD", 0.96, 1, ["refund", "approved", "ssn"]),
                ("alert@metamask-wallet-freeze.com", "CRITICAL: Suspicious Withdrawal Detected", "1.45 BTC withdrawal initiated. Freeze transaction at http://binance-security-alert.io/freeze.", True, 0.96, "CRITICAL", "CRYPTO_INVESTMENT_SCAM", 0.98, 1, ["critical", "withdrawal", "freeze"]),
                ("dhl-status@dhl-parcel-delivery-fee.com", "DHL Delivery Failed: Package Held", "Pay $2.99 redelivery fee at http://dhl-parcel-delivery-fee.com to release parcel.", True, 0.88, "HIGH", "TRANSACTION_FRAUD", 0.89, 1, ["delivery failed", "held", "pay"]),
                ("storage-admin@google-drive-storage-renew.xyz", "Storage Full: 50GB Files Will Be Purged", "Upgrade cloud quota for $1.99 at http://google-drive-storage-renew.xyz or files will be deleted.", True, 0.87, "HIGH", "ENTERTAINMENT_SCAM", 0.88, 1, ["storage full", "purged", "deleted"]),
                ("bank-auth@secure-account-update.xyz", "Wells Fargo: Account Suspension Notice", "Your debit card is suspended due to suspicious activity. Verify at http://auth-identity-check.com.", True, 0.93, "HIGH", "BANKING_FRAUD", 0.94, 1, ["suspended", "verify"]),
                ("it-helpdesk@sso-login-update.tech", "Urgent: VPN Client Security Update Required", "All employees must install the security patch from http://vpn-update-portal.info/patch.exe.", True, 0.95, "CRITICAL", "ACCOUNT_VERIFICATION_SCAM", 0.92, 1, ["urgent", "security patch"]),
                ("crypto-alert@wallet-restore-key.site", "Trust Wallet Backup Key Verification", "Re-validate your 12-word seed phrase at http://wallet-restore-key.site to avoid account lockout.", True, 0.98, "CRITICAL", "CRYPTO_INVESTMENT_SCAM", 0.97, 1, ["verification", "seed phrase"]),
                
                # Legitimate emails
                ("prof.smith@university.edu", "Network Security Project Submission Guidelines", "Dear Students, Please review the capstone project submission guidelines on the course portal.", False, 0.04, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("notifications@github.com", "[GitHub] Security advisory for dependency upgrade", "Hi Developer, Dependabot opened a security PR for package updates in your repository.", False, 0.05, "LOW", "LEGITIMATE", 1.0, 1, []),
                ("team-lead@techcorp.com", "Weekly Sprint Planning & Architecture Meeting", "Hi Team, Tomorrow at 10 AM we will discuss API performance and microservice deployments.", False, 0.02, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("hr-announcements@corp.org", "Quarterly Employee Wellness & Holiday Schedule", "Please review the updated holiday calendar for the upcoming quarter on the HR intranet.", False, 0.03, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("billing@aws.amazon.com", "Your Monthly AWS Cloud Invoice Statement", "Your monthly AWS invoice for account #8491 is $14.20. View details in console.", False, 0.08, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("support@stackoverflow.com", "Weekly Technical Newsletter: Machine Learning & Python", "Top voted answers: How to optimize TF-IDF vectorizer parameters in scikit-learn.", False, 0.06, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("conference-chair@ieee-security.org", "Acceptance Notification: IEEE Security & Privacy", "We are pleased to inform you that your paper has been accepted for presentation.", False, 0.01, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("library-system@university.edu", "Book Reservation Confirmation: Applied Cryptography", "Your reserved copy of Applied Cryptography is ready for pickup at circulation desk.", False, 0.02, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("colleague@techcorp.com", "Code Review Request for Pull Request #42", "Hey, could you check my PR for the authentication middleware refactoring when you have time?", False, 0.03, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("newsletter@pythondigest.org", "Python Weekly Digest Issue #640", "Latest articles on FastAPI background tasks, Pydantic v2 migrations, and scikit-learn 1.4 features.", False, 0.05, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("admin@cybersec-conference.com", "Registration Confirmation for Security Summit", "Thank you for registering for the National Cybersecurity Summit. Badge details attached.", False, 0.04, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("advisor@university.edu", "Academic Advising Session Scheduled", "Your advising appointment for next semester course selection is confirmed for Tuesday 2 PM.", False, 0.02, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("helpdesk@internal-portal.corp", "Scheduled Server Maintenance Notice", "Server maintenance will take place this Sunday from 2 AM to 4 AM UTC. Expect minor downtime.", False, 0.05, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("recruiter@techjobs.com", "Invitation for Senior Security Engineer Interview", "We reviewed your application and would like to schedule an initial technical screening.", False, 0.09, "LOW", "LEGITIMATE", 1.0, 0, []),
                ("alumni@university.edu", "Annual Engineering Alumni Network Gathering", "Join us for our annual networking event next month at the campus auditorium.", False, 0.03, "LOW", "LEGITIMATE", 1.0, 0, [])
            ]
            
            start_date = datetime.utcnow() - timedelta(days=14)
            for idx, item in enumerate(sample_emails):
                sender, subject, body, is_phish, conf, r_level, cat, cat_conf, u_cnt, kws = item
                recv_date = start_date + timedelta(days=idx // 2, hours=random.randint(0, 12), minutes=random.randint(0, 59))
                
                db_e = Email(
                    user_id=admin_user.id,
                    sender=sender,
                    subject=subject,
                    body=body,
                    received_at=recv_date,
                    is_phishing=is_phish,
                    confidence=conf,
                    risk_level=r_level,
                    phishing_category=cat,
                    category_confidence=cat_conf,
                    url_count=u_cnt,
                    suspicious_keywords=json.dumps(kws),
                    headers_json=json.dumps({"has_spf": True if not is_phish else False, "has_dkim": True if not is_phish else False, "has_dmarc": True if not is_phish else False, "auth_warning": "" if not is_phish else "Missing authentication"})
                )
                db.add(db_e)
            db.commit()
            print("Successfully seeded 25 email records.")

    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    """Initialize ML models and database tables/seeders on application startup."""
    print("Starting Phishing Email Risk Prediction System Backend...")
    try:
        # Initialize ML Models
        PhishingDetectorService.get_model()
        RiskPredictorService.get_model()
        
        # Check / Train DistilBERT Category Model if missing
        category_model_dir = os.path.join(os.path.dirname(__file__), "ml", "category_model")
        if not os.path.exists(category_model_dir) or not os.path.exists(os.path.join(category_model_dir, "config.json")):
            print("Category model missing at startup. Running DistilBERT category classifier training...")
            try:
                from .ml.train_category_classifier import train
                train()
            except Exception as train_err:
                print(f"Notice: Auto-training category model skipped/failed ({train_err}). API will operate in fallback mode.")
        
        # Seed Database
        seed_database()
        print("Backend startup initialization completed successfully!")
    except Exception as e:

        print(f"Error during startup initialization: {e}")

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "Phishing Email Risk Prediction System",
        "documentation": "/docs",
        "version": "1.0.0"
    }
