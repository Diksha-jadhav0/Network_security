import os
import csv
import random
from datetime import datetime, timedelta

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))

PHISHING_TEMPLATES = [
    {
        "sender": "security-alert@{domain}",
        "subject": "URGENT: Your {bank} account has been suspended",
        "body": "Dear customer, We detected unauthorized login attempts on your {bank} account. To restore full access, verify your identity immediately by visiting http://{phish_domain}/login-verify?id={rand_id}. Failure to verify within 24 hours will result in permanent account termination. Security Team",
        "phish_domains": ["paypa1-security.com", "bank-verification-online.net", "secure-account-update.xyz", "auth-identity-check.com"],
        "urgent_keywords": ["urgent", "suspended", "verify", "unauthorized", "termination"]
    },
    {
        "sender": "payroll-update@{domain}",
        "subject": "Action Required: Update Direct Deposit Information",
        "body": "Attention Employee, Your recent salary deposit failed due to invalid bank routing details. Please click http://{phish_domain}/payroll/update to update your payment portal credentials and prevent salary delays. HR Payroll Department",
        "phish_domains": ["company-payroll-portal.info", "hr-direct-deposit.tech", "employee-benefits-login.com"],
        "urgent_keywords": ["action required", "deposit", "failed", "update", "credentials"]
    },
    {
        "sender": "it-support@{domain}",
        "subject": "Office 365 Password Expiration Alert",
        "body": "Your Microsoft Office 365 password expires today. Keep your current password by confirming your current credentials at http://{phish_domain}/auth/sso?user=token. If not verified, your inbox will be locked. IT Help Desk",
        "phish_domains": ["office365-password-reset.com", "microsoft-sso-verify.net", "login-microsoftonline-sec.org"],
        "urgent_keywords": ["password", "expiration", "locked", "credentials", "verify"]
    },
    {
        "sender": "tax-refund@{domain}",
        "subject": "Internal Revenue Service: You have an pending refund of $1,420.00",
        "body": "Congratulations! The IRS tax refund division approved your tax rebate application. Access http://192.168.1.105/irs/claim-refund to submit your social security number and debit card details. Federal Tax Division",
        "phish_domains": ["192.168.1.105", "irs-government-tax-refund.top", "claim-tax-rebate2026.online"],
        "urgent_keywords": ["refund", "approved", "ssn", "debit card", "claim"]
    },
    {
        "sender": "crypto-guard@{domain}",
        "subject": "CRITICAL: Security Breach Detected in Wallet",
        "body": "Suspicious withdrawal of 1.45 BTC detected from your MetaMask wallet. If this was not you, freeze your transaction immediately at http://{phish_domain}/crypto/freeze-funds. Seed phrase re-validation required. Binance Security",
        "phish_domains": ["metamask-wallet-freeze.com", "binance-security-alert.io", "crypto-vault-protect.site"],
        "urgent_keywords": ["critical", "withdrawal", "freeze", "seed phrase", "security breach"]
    },
    {
        "sender": "delivery-status@{domain}",
        "subject": "DHL Delivery Failed: Package #94827104 Held at Warehouse",
        "body": "We tried to deliver your parcel today but no one was present. Pay the re-delivery fee of $2.99 at http://{phish_domain}/dhl/parcel-tracking to reschedule parcel dispatch. Customer Care",
        "phish_domains": ["dhl-parcel-delivery-fee.com", "fedex-package-redelivery.org", "usps-post-redelivery.info"],
        "urgent_keywords": ["delivery failed", "held", "pay", "parcel", "reschedule"]
    },
    {
        "sender": "cloud-storage-admin@{domain}",
        "subject": "Storage Full: 50GB Google Drive Files Will Be Deleted",
        "body": "Your cloud storage subscription expired. Upgrade now for $1.99 or your photos and documents will be permanently purged in 12 hours: http://{phish_domain}/drive/extend-plan. Google Cloud Admin",
        "phish_domains": ["google-drive-storage-renew.xyz", "cloud-storage-billing.tech", "icloud-quota-upgrade.click"],
        "urgent_keywords": ["storage full", "deleted", "purged", "upgrade", "expired"]
    },
    {
        "sender": "university-registrar@{domain}",
        "subject": "Immediate Warning: Student Portal Access Revoked",
        "body": "Your university library fees are overdue. Failure to clear dues at http://{phish_domain}/portal/fee-payment will prevent final examination registration. Student Affairs Office",
        "phish_domains": ["university-fee-portal.net", "student-records-update.online", "edu-portal-verify.site"],
        "urgent_keywords": ["warning", "overdue", "revoked", "dues", "payment"]
    }
]

LEGITIMATE_TEMPLATES = [
    {
        "sender": "prof.smith@university.edu",
        "subject": "Network Security Project Submission Deadline & Guidelines",
        "body": "Dear Students, Please find attached the final guidelines for the Network Security capstone project. Submissions are due next Friday by 5 PM via the official university learning portal. Let me know if you have questions during office hours. Best regards, Dr. Smith",
        "legit_domains": ["university.edu"],
        "urgent_keywords": []
    },
    {
        "sender": "notifications@github.com",
        "subject": "[GitHub] Security advisory for dependency upgrade in main branch",
        "body": "Hi Developer, We detected a non-critical update for your repository. Please review the pull request on GitHub to merge the patch. You can review diffs at https://github.com/repository/pulls. Happy coding!",
        "legit_domains": ["github.com"],
        "urgent_keywords": []
    },
    {
        "sender": "team-lead@techcorp.com",
        "subject": "Weekly Sprint Planning & Architecture Review Meeting",
        "body": "Hi Team, Tomorrow at 10 AM we will hold our weekly sprint meeting via Google Meet. Agenda includes REST API refactoring, frontend dashboard design, and test coverage metrics. Please prepare your progress slides. Cheers, Alex",
        "legit_domains": ["techcorp.com"],
        "urgent_keywords": []
    },
    {
        "sender": "hr-announcements@corp.org",
        "subject": "Quarterly Employee Wellness & Holiday Schedule",
        "body": "Hello Everyone, Please review the attached company holiday calendar for the upcoming quarter. We are excited to announce our annual wellness week featuring virtual workshops and fitness sessions. Regards, Human Resources",
        "legit_domains": ["corp.org"],
        "urgent_keywords": []
    },
    {
        "sender": "billing@aws.amazon.com",
        "subject": "Your Monthly AWS Cloud Invoice Statement - Account #849102",
        "body": "Dear Customer, Your monthly AWS usage summary for account ending in 8491 is now available. Total amount charged to credit card on file: $14.20. View your full billing breakdown in the AWS Management Console.",
        "legit_domains": ["amazon.com"],
        "urgent_keywords": []
    },
    {
        "sender": "support@stackoverflow.com",
        "subject": "Weekly Technical Newsletter: Machine Learning in Python & Cybersecurity",
        "body": "Here are top voted answers on StackOverflow this week: 1. How to optimize TF-IDF vectorizer parameters in scikit-learn. 2. Securing FastAPI endpoints with JWT tokens. Read more on the official blog.",
        "legit_domains": ["stackoverflow.com"],
        "urgent_keywords": []
    },
    {
        "sender": "conference-chair@ieee-security.org",
        "subject": "Acceptance Notification: IEEE Network Security & Privacy Workshop",
        "body": "Dear Author, We are pleased to inform you that your paper titled 'Machine Learning for Phishing Risk Score Analytics' has been accepted for oral presentation at the upcoming IEEE workshop. Registration instructions attached.",
        "legit_domains": ["ieee-security.org"],
        "urgent_keywords": []
    },
    {
        "sender": "library-system@university.edu",
        "subject": "Book Reservation Confirmation: Applied Cryptography 2nd Ed.",
        "body": "Your reserved title 'Applied Cryptography' by Bruce Schneier is ready for pickup at the Main Library circulation desk. Reserved until Friday 4 PM.",
        "legit_domains": ["university.edu"],
        "urgent_keywords": []
    }
]

DOMAINS = ["mail-server.com", "fast-connect.net", "global-net.org", "service-update.info"]
BANKS = ["PayPal", "Chase Bank", "Wells Fargo", "Bank of America", "Citibank"]

def generate_phishing_emails(count=250):
    emails = []
    for i in range(count):
        tmpl = random.choice(PHISHING_TEMPLATES)
        phish_dom = random.choice(tmpl["phish_domains"])
        sender_dom = random.choice(DOMAINS)
        sender = tmpl["sender"].format(domain=sender_dom)
        bank = random.choice(BANKS)
        rand_id = str(random.randint(10000, 99999))
        
        subject = tmpl["subject"].format(bank=bank)
        body = tmpl["body"].format(bank=bank, phish_domain=phish_dom, rand_id=rand_id)
        
        emails.append({
            "email_id": f"PHISH_{i+1:04d}",
            "sender": sender,
            "subject": subject,
            "body": body,
            "is_phishing": 1,
            "label": "phishing"
        })
    return emails

def generate_legitimate_emails(count=250):
    emails = []
    for i in range(count):
        tmpl = random.choice(LEGITIMATE_TEMPLATES)
        emails.append({
            "email_id": f"LEGIT_{i+1:04d}",
            "sender": tmpl["sender"],
            "subject": tmpl["subject"],
            "body": tmpl["body"],
            "is_phishing": 0,
            "label": "legitimate"
        })
    return emails

def generate_user_history(count=200):
    history = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        recv_time = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        is_phish = 1 if random.random() < 0.35 else 0
        
        if is_phish:
            tmpl = random.choice(PHISHING_TEMPLATES)
            phish_dom = random.choice(tmpl["phish_domains"])
            sender = tmpl["sender"].format(domain=random.choice(DOMAINS))
            subject = tmpl["subject"].format(bank="Secure Bank")
            body = tmpl["body"].format(bank="Secure Bank", phish_domain=phish_dom, rand_id=str(random.randint(1000, 9999)))
            confidence = round(random.uniform(0.85, 0.99), 2)
            url_count = random.randint(1, 4)
        else:
            tmpl = random.choice(LEGITIMATE_TEMPLATES)
            sender = tmpl["sender"]
            subject = tmpl["subject"]
            body = tmpl["body"]
            confidence = round(random.uniform(0.01, 0.15), 2)
            url_count = random.randint(0, 1)

        history.append({
            "history_id": f"HIST_{i+1:04d}",
            "user_email": "admin@example.com",
            "sender": sender,
            "subject": subject,
            "body": body,
            "received_at": recv_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_phishing": is_phish,
            "confidence": confidence,
            "url_count": url_count,
            "is_off_hours": 1 if (recv_time.hour < 7 or recv_time.hour > 20) else 0
        })
    return history

def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    phish_data = generate_phishing_emails(250)
    legit_data = generate_legitimate_emails(250)
    history_data = generate_user_history(200)

    # Write phishing CSV
    phish_csv = os.path.join(DATASET_DIR, "phishing_emails.csv")
    with open(phish_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_id", "sender", "subject", "body", "is_phishing", "label"])
        writer.writeheader()
        writer.writerows(phish_data)

    # Write legitimate CSV
    legit_csv = os.path.join(DATASET_DIR, "legitimate_emails.csv")
    with open(legit_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_id", "sender", "subject", "body", "is_phishing", "label"])
        writer.writeheader()
        writer.writerows(legit_data)

    # Write history CSV
    hist_csv = os.path.join(DATASET_DIR, "user_history_sample.csv")
    with open(hist_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["history_id", "user_email", "sender", "subject", "body", "received_at", "is_phishing", "confidence", "url_count", "is_off_hours"])
        writer.writeheader()
        writer.writerows(history_data)

    print(f"Generated {len(phish_data)} phishing emails -> {phish_csv}")
    print(f"Generated {len(legit_data)} legitimate emails -> {legit_csv}")
    print(f"Generated {len(history_data)} user history samples -> {hist_csv}")

if __name__ == "__main__":
    main()
