import os
import sys
import csv
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

ML_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(ML_DIR))
DATASET_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "dataset")

def ensure_dataset():
    """Ensure dataset CSVs exist or generate them."""
    phish_path = os.path.join(DATASET_DIR, "phishing_emails.csv")
    legit_path = os.path.join(DATASET_DIR, "legitimate_emails.csv")
    
    if not (os.path.exists(phish_path) and os.path.exists(legit_path)):
        print("Dataset CSVs missing. Invoking dataset generator...")
        gen_script = os.path.join(DATASET_DIR, "generate_dataset.py")
        if os.path.exists(gen_script):
            import subprocess
            subprocess.run([sys.executable, gen_script], check=True)
        else:
            raise FileNotFoundError(f"Cannot find generator script at {gen_script}")
    return phish_path, legit_path

def train_and_save_classifier():
    """Train TF-IDF + Random Forest Phishing Classifier."""
    phish_path, legit_path = ensure_dataset()
    
    df_phish = pd.read_csv(phish_path)
    df_legit = pd.read_csv(legit_path)
    
    df = pd.concat([df_phish, df_legit], ignore_index=True)
    df["full_text"] = df["sender"].fillna("") + " " + df["subject"].fillna("") + " " + df["body"].fillna("")
    
    X = df["full_text"]
    y = df["is_phishing"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))),
        ('rf', RandomForestClassifier(n_estimators=200, random_state=42, max_depth=20, n_jobs=-1))
    ])
    
    print("Training Phishing Classifier Pipeline (TF-IDF + Random Forest)...")
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\n" + "="*50)
    print("PHISHING CLASSIFIER EVALUATION METRICS")
    print("="*50)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("="*50 + "\n")
    
    model_path = os.path.join(ML_DIR, "phishing_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Successfully saved phishing model -> {model_path}")
    return acc, prec, rec, f1, roc_auc

if __name__ == "__main__":
    train_and_save_classifier()
