import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

ML_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_synthetic_behavioral_dataset(samples=1000):
    """
    Generate synthetic historical behavioral feature vectors for training the
    Future Risk Prediction Logistic Regression Model.
    
    Features:
    0: phishing_last_24h (int 0-10)
    1: phishing_last_7d (int 0-30)
    2: unknown_sender_ratio (float 0.0-1.0)
    3: avg_url_count (float 0.0-5.0)
    4: urgent_keyword_frequency (float 0.0-10.0)
    5: suspicious_domain_frequency (float 0.0-10.0)
    6: off_hours_email_ratio (float 0.0-1.0)
    """
    np.random.seed(42)
    
    phishing_last_24h = np.random.poisson(lam=1.2, size=samples)
    phishing_last_7d = phishing_last_24h * 4 + np.random.poisson(lam=3.0, size=samples)
    unknown_sender_ratio = np.clip(np.random.beta(a=2, b=5, size=samples), 0.0, 1.0)
    avg_url_count = np.clip(np.random.normal(loc=1.5, scale=0.8, size=samples), 0.0, 6.0)
    urgent_keyword_frequency = np.clip(np.random.poisson(lam=1.5, size=samples), 0, 10)
    suspicious_domain_frequency = np.clip(np.random.poisson(lam=1.2, size=samples), 0, 10)
    off_hours_email_ratio = np.clip(np.random.beta(a=2, b=4, size=samples), 0.0, 1.0)
    
    # Calculate a realistic logit risk formula to generate ground truth labels
    risk_score = (
        0.35 * phishing_last_24h +
        0.15 * phishing_last_7d +
        1.5 * unknown_sender_ratio +
        0.4 * avg_url_count +
        0.3 * urgent_keyword_frequency +
        0.4 * suspicious_domain_frequency +
        1.2 * off_hours_email_ratio - 2.5
    )
    
    prob = 1 / (1 + np.exp(-risk_score))
    y = (prob > 0.45).astype(int)
    
    df = pd.DataFrame({
        "phishing_last_24h": phishing_last_24h,
        "phishing_last_7d": phishing_last_7d,
        "unknown_sender_ratio": unknown_sender_ratio,
        "avg_url_count": avg_url_count,
        "urgent_keyword_frequency": urgent_keyword_frequency,
        "suspicious_domain_frequency": suspicious_domain_frequency,
        "off_hours_email_ratio": off_hours_email_ratio,
        "target_risk": y
    })
    
    return df

def train_and_save_risk_model():
    """Train Logistic Regression Model for future 24h phishing risk prediction."""
    print("Generating synthetic behavioral feature dataset...")
    df = generate_synthetic_behavioral_dataset(1200)
    
    feature_cols = [
        "phishing_last_24h",
        "phishing_last_7d",
        "unknown_sender_ratio",
        "avg_url_count",
        "urgent_keyword_frequency",
        "suspicious_domain_frequency",
        "off_hours_email_ratio"
    ]
    
    X = df[feature_cols]
    y = df["target_risk"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training Future Risk Prediction Model (Logistic Regression)...")
    model = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\n" + "="*50)
    print("FUTURE RISK PREDICTION MODEL EVALUATION METRICS")
    print("="*50)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("="*50 + "\n")
    
    model_path = os.path.join(ML_DIR, "risk_model.pkl")
    joblib.dump(model, model_path)
    print(f"Successfully saved risk model -> {model_path}")
    return acc, prec, rec, f1, roc_auc

if __name__ == "__main__":
    train_and_save_risk_model()
