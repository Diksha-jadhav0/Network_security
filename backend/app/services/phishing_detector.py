import os
import sys
import joblib
from typing import Dict, Any, List
from .feature_engineering import FeatureEngineeringService

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")
MODEL_PATH = os.path.join(ML_DIR, "phishing_model.pkl")

class PhishingDetectorService:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy load or train the TF-IDF + Random Forest model."""
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                print("Phishing model pkl not found. Training model automatically...")
                train_script = os.path.join(ML_DIR, "train_classifier.py")
                import subprocess
                subprocess.run([sys.executable, train_script], check=True)
            
            cls._model = joblib.load(MODEL_PATH)
        return cls._model

    @classmethod
    def analyze_email(cls, sender: str, subject: str, body: str, urls: List[str] = None, attachments: List[str] = None, reply_to: str = "") -> Dict[str, Any]:
        """
        Detect whether an email is phishing or legitimate, returning confidence score & risk details.
        """
        urls = urls or []
        attachments = attachments or []
        
        # Extract engineered features
        features = FeatureEngineeringService.extract_features(
            sender=sender,
            subject=subject,
            body=body,
            urls=urls,
            attachments=attachments,
            reply_to=reply_to
        )
        
        full_text = f"{sender} {subject} {body}"
        
        # Model inference
        model = cls.get_model()
        ml_prob = float(model.predict_proba([full_text])[0][1])
        
        # Calculate heuristic adjustment boosts
        boost = 0.0
        if features["has_ip_address_url"]:
            boost += 0.20
        if features["sender_domain_mismatch"]:
            boost += 0.25
        if features["attachment_exe"]:
            boost += 0.30
        if features["urgent_word_count"] >= 3:
            boost += 0.15
        elif features["urgent_word_count"] >= 1:
            boost += 0.05
        if features["is_suspicious_domain"]:
            boost += 0.15
        if features["uppercase_ratio"] > 0.30:
            boost += 0.10

        final_confidence = min(0.99, max(0.01, ml_prob + boost if ml_prob > 0.3 else ml_prob))
        is_phishing = final_confidence >= 0.50
        
        if final_confidence >= 0.85:
            risk_level = "CRITICAL" if (features["attachment_exe"] or features["has_ip_address_url"]) else "HIGH"
        elif final_confidence >= 0.50:
            risk_level = "HIGH"
        elif final_confidence >= 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "is_phishing": is_phishing,
            "confidence": round(final_confidence, 2),
            "risk_level": risk_level,
            "suspicious_keywords": features["urgent_words"],
            "url_count": features["url_count"],
            "sender_domain_analysis": {
                "domain": features["sender_domain"],
                "is_suspicious": features["is_suspicious_domain"],
                "is_mismatched": features["sender_domain_mismatch"],
                "has_ip_url": features["has_ip_address_url"]
            },
            "features": features
        }
