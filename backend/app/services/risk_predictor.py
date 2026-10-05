import os
import sys
import joblib
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models import Email

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")
RISK_MODEL_PATH = os.path.join(ML_DIR, "risk_model.pkl")

class RiskPredictorService:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy load or train the Logistic Regression risk prediction model."""
        if cls._model is None:
            if not os.path.exists(RISK_MODEL_PATH):
                print("Risk model pkl not found. Training model automatically...")
                train_script = os.path.join(ML_DIR, "train_risk_model.py")
                import subprocess
                subprocess.run([sys.executable, train_script], check=True)
            
            cls._model = joblib.load(RISK_MODEL_PATH)
        return cls._model

    @classmethod
    def predict_user_risk(cls, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calculate historical behavioral statistics for a user and predict future phishing exposure risk.
        """
        now = datetime.utcnow()
        last_24h_time = now - timedelta(days=1)
        last_7d_time = now - timedelta(days=7)
        
        user_emails = db.query(Email).filter(Email.user_id == user_id).all()
        
        total_emails = len(user_emails)
        if total_emails == 0:
            return {
                "user_id": user_id,
                "future_risk_probability": 0.05,
                "predicted_risk": "LOW",
                "features_used": {
                    "phishing_last_24h": 0,
                    "phishing_last_7d": 0,
                    "unknown_sender_ratio": 0.0,
                    "avg_url_count": 0.0,
                    "urgent_keyword_frequency": 0.0,
                    "suspicious_domain_frequency": 0.0,
                    "off_hours_email_ratio": 0.0
                },
                "recommendation": "Insufficient email history recorded. Continue analyzing emails to build threat intelligence profile."
            }

        # Calculate historical features
        phishing_last_24h = 0
        phishing_last_7d = 0
        total_urls = 0
        urgent_keywords_count = 0
        suspicious_domain_count = 0
        off_hours_count = 0
        unknown_sender_count = 0

        known_domains = {"company.com", "university.edu", "github.com", "google.com", "microsoft.com"}

        for email in user_emails:
            recv_at = email.received_at or email.created_at
            
            if email.is_phishing:
                if recv_at >= last_24h_time:
                    phishing_last_24h += 1
                if recv_at >= last_7d_time:
                    phishing_last_7d += 1
            
            total_urls += (email.url_count or 0)
            
            # Check keywords
            if email.suspicious_keywords:
                try:
                    kw_list = json.loads(email.suspicious_keywords) if email.suspicious_keywords.startswith("[") else email.suspicious_keywords.split(",")
                    urgent_keywords_count += len(kw_list)
                except Exception:
                    pass

            # Check domain
            domain = email.sender.split("@")[-1].lower() if "@" in email.sender else ""
            if domain and domain not in known_domains:
                unknown_sender_count += 1
            
            suspicious_tlds = [".xyz", ".top", ".info", ".click", ".tech", ".site", ".online"]
            if any(domain.endswith(tld) for tld in suspicious_tlds) or "paypa1" in domain or "bank" in domain:
                suspicious_domain_count += 1

            # Check off hours (<7am or >8pm)
            hour = recv_at.hour
            if hour < 7 or hour > 20:
                off_hours_count += 1

        unknown_sender_ratio = round(unknown_sender_count / total_emails, 2)
        avg_url_count = round(total_urls / total_emails, 2)
        urgent_keyword_freq = round(urgent_keywords_count / total_emails, 2)
        suspicious_domain_freq = round(suspicious_domain_count / total_emails, 2)
        off_hours_ratio = round(off_hours_count / total_emails, 2)

        feature_vector = np.array([[
            phishing_last_24h,
            phishing_last_7d,
            unknown_sender_ratio,
            avg_url_count,
            urgent_keyword_freq,
            suspicious_domain_freq,
            off_hours_ratio
        ]])

        model = cls.get_model()
        risk_prob = float(model.predict_proba(feature_vector)[0][1])
        
        # Determine risk tier & recommendation
        if risk_prob >= 0.70:
            predicted_risk = "HIGH"
            recommendation = "HIGH THREAT ALERT: High phishing volume detected in recent 24-72 hours. Exercise extreme caution, avoid opening links or attachments from unknown domains."
        elif risk_prob >= 0.35:
            predicted_risk = "MEDIUM"
            recommendation = "ELEVATED RISK: Multiple suspicious email patterns detected. Double check sender email headers and SPF/DKIM verification before clicking links."
        else:
            predicted_risk = "LOW"
            recommendation = "NORMAL STATUS: Low threat exposure based on recent historical email behavior. Remain vigilant against credential harvesting."

        return {
            "user_id": user_id,
            "future_risk_probability": round(risk_prob, 2),
            "predicted_risk": predicted_risk,
            "features_used": {
                "phishing_last_24h": phishing_last_24h,
                "phishing_last_7d": phishing_last_7d,
                "unknown_sender_ratio": unknown_sender_ratio,
                "avg_url_count": avg_url_count,
                "urgent_keyword_frequency": urgent_keyword_freq,
                "suspicious_domain_frequency": suspicious_domain_freq,
                "off_hours_email_ratio": off_hours_ratio
            },
            "recommendation": recommendation
        }
