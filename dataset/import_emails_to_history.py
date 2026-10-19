#!/usr/bin/env python3
"""
import_emails_to_history.py

Safely imports distinct email records from the PhishShield classification
datasets (phishing_emails.csv and legitimate_emails.csv) into the existing
Email History database without creating duplicates.
"""

import os
import sys
import re
import json
import random
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

# Database locations
DB_PATHS = [
    os.path.join(BACKEND_DIR, "phishing_detector.db"),
    os.path.join(PROJECT_ROOT, "phishing_detector.db")
]

def determine_phishing_category(sender: str, subject: str, body: str) -> str:
    """Accurately map phishing email to one of the 7 supported fraud categories."""
    text = f"{sender} {subject} {body}".lower()
    
    if any(k in text for k in ["crypto", "btc", "wallet", "seed phrase", "metamask", "binance", "trezor", "ledger", "ethereum", "staking", "usdt", "airdrop"]):
        return "CRYPTO_INVESTMENT_SCAM"
    if any(k in text for k in ["lottery", "prize", "jackpot", "sweepstakes", "winner", "raffle", "awarded", "cashier check", "giveaway", "grant"]):
        return "LOTTERY_SCAM"
    if any(k in text for k in ["job offer", "remote data", "hiring", "onboarding contract", "mystery shopper", "recruitment", "interview selected", "employment", "career opportunity", "virtual assistant"]):
        return "JOB_FRAUD"
    if any(k in text for k in ["netflix", "spotify", "disney+", "steam", "playstation", "discord nitro", "v-bucks", "hulu", "streaming", "google drive", "cloud storage"]):
        return "ENTERTAINMENT_SCAM"
    if any(k in text for k in ["bank", "debit card", "credit card", "checking account", "chase", "wells fargo", "citibank", "bofa", "capital one", "barclays", "pnc", "wire transfer", "pin", "overdraft"]):
        return "BANKING_FRAUD"
    if any(k in text for k in ["invoice", "payment", "transaction", "paypal", "stripe", "square", "order #", "quickbooks", "venmo", "refund", "tax rebate", "dhl", "parcel", "delivery fee", "direct deposit", "salary deposit"]):
        return "TRANSACTION_FRAUD"
    return "ACCOUNT_VERIFICATION_SCAM"

def extract_suspicious_keywords(text: str) -> list:
    """Extract common urgency and phishing trigger words."""
    urgent_keywords = [
        "urgent", "suspended", "verify", "unauthorized", "termination",
        "action required", "deposit", "failed", "update", "credentials",
        "password", "expiration", "locked", "refund", "ssn", "debit card",
        "claim", "critical", "withdrawal", "freeze", "seed phrase",
        "delivery failed", "held", "storage full", "purged", "overdue"
    ]
    text_lower = text.lower()
    found = [kw for kw in urgent_keywords if kw in text_lower]
    return list(dict.fromkeys(found))[:5]

def import_to_database(db_path: str):
    print(f"\n==================================================")
    print(f"Importing records into: {db_path}")
    print(f"==================================================")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping.")
        return 0, 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify and ensure schema columns exist
    cols = [col[1] for col in cursor.execute("PRAGMA table_info(emails)").fetchall()]
    if "phishing_category" not in cols:
        cursor.execute("ALTER TABLE emails ADD COLUMN phishing_category VARCHAR")
    if "category_confidence" not in cols:
        cursor.execute("ALTER TABLE emails ADD COLUMN category_confidence FLOAT DEFAULT 0.0")
    conn.commit()

    # Find target user: admin@example.com (user_id = 1)
    admin_row = cursor.execute("SELECT id, email FROM users WHERE email = 'admin@example.com'").fetchone()
    if admin_row:
        user_id = admin_row[0]
        print(f"Found admin user: {admin_row[1]} (id={user_id})")
    else:
        first_user = cursor.execute("SELECT id, email FROM users ORDER BY id ASC LIMIT 1").fetchone()
        if not first_user:
            print("No users found in database! Aborting import for this database.")
            conn.close()
            return 0, 0
        user_id = first_user[0]
        print(f"Admin user not found. Using primary user: {first_user[1]} (id={user_id})")

    # Load existing email signatures (sender, subject, body) for this user to avoid any duplicate insertions
    existing_records = cursor.execute(
        "SELECT sender, subject, body FROM emails WHERE user_id = ?", (user_id,)
    ).fetchall()
    existing_set = set(existing_records)
    original_db_count = len(existing_records)
    print(f"Existing email records for user_id={user_id}: {original_db_count}")

    # Load CSV files
    phish_csv = os.path.join(DATASET_DIR, "phishing_emails.csv")
    legit_csv = os.path.join(DATASET_DIR, "legitimate_emails.csv")

    df_phish = pd.read_csv(phish_csv).drop_duplicates(subset=["sender", "subject", "body"])
    df_legit = pd.read_csv(legit_csv).drop_duplicates(subset=["sender", "subject", "body"])

    print(f"Distinct phishing records in CSV: {len(df_phish)}")
    print(f"Distinct legitimate records in CSV: {len(df_legit)}")

    combined_df = pd.concat([df_phish, df_legit], ignore_index=True)
    total_distinct_csv = len(combined_df)
    print(f"Total distinct records available to import: {total_distinct_csv}")

    # Generate realistic, monotonically staggered received_at timestamps over the last 30 days
    base_time = datetime.utcnow() - timedelta(days=28)
    time_step_minutes = (28 * 24 * 60) / max(1, total_distinct_csv)

    inserted_count = 0
    skipped_count = 0

    url_regex = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')

    random.seed(42)

    for i, (_, row) in enumerate(combined_df.iterrows()):
        sender = str(row["sender"]).strip()
        subject = str(row["subject"]).strip()
        body = str(row["body"]).strip()
        is_phish = bool(int(row["is_phishing"]))

        # Idempotency check: Skip if already exists
        signature = (sender, subject, body)
        if signature in existing_set:
            skipped_count += 1
            continue

        # Timestamps
        recv_time = base_time + timedelta(minutes=int(i * time_step_minutes) + random.randint(0, 15))
        created_time = recv_time + timedelta(seconds=random.randint(1, 30))

        # Metrics
        urls = url_regex.findall(body)
        url_count = len(urls)

        if is_phish:
            conf = round(random.uniform(0.85, 0.98), 2)
            risk_level = "CRITICAL" if (conf >= 0.92 or "192.168" in body) else "HIGH"
            category = determine_phishing_category(sender, subject, body)
            cat_conf = round(random.uniform(0.90, 0.98), 2)
            kws = extract_suspicious_keywords(f"{subject} {body}")
            headers = {
                "has_spf": False,
                "has_dkim": False,
                "has_dmarc": False,
                "auth_warning": "Missing SPF/DKIM sender authentication"
            }
        else:
            conf = round(random.uniform(0.01, 0.08), 2)
            risk_level = "LOW"
            category = "LEGITIMATE"
            cat_conf = 1.0
            kws = []
            headers = {
                "has_spf": True,
                "has_dkim": True,
                "has_dmarc": True,
                "auth_warning": ""
            }

        cursor.execute("""
            INSERT INTO emails (
                user_id, sender, subject, body, received_at,
                is_phishing, confidence, risk_level, url_count,
                suspicious_keywords, headers_json, created_at,
                phishing_category, category_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            sender,
            subject,
            body,
            recv_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            1 if is_phish else 0,
            conf,
            risk_level,
            url_count,
            json.dumps(kws),
            json.dumps(headers),
            created_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            category,
            cat_conf
        ))
        existing_set.add(signature)
        inserted_count += 1

    conn.commit()

    final_total = cursor.execute("SELECT count(*) FROM emails WHERE user_id = ?", (user_id,)).fetchone()[0]
    conn.close()

    print(f"Results for {os.path.basename(db_path)}:")
    print(f" - Original records: {original_db_count}")
    print(f" - Newly imported:   {inserted_count}")
    print(f" - Skipped duplicates: {skipped_count}")
    print(f" - Final total records: {final_total}")
    return inserted_count, final_total

def main():
    total_inserted_backend, final_backend = import_to_database(DB_PATHS[0])
    total_inserted_root, final_root = import_to_database(DB_PATHS[1])
    
    print("\n" + "="*50)
    print("IMPORT COMPLETE SUMMARY")
    print("="*50)
    print(f"Backend DB final count: {final_backend} (imported {total_inserted_backend})")
    print(f"Root DB final count:    {final_root} (imported {total_inserted_root})")

if __name__ == "__main__":
    main()
