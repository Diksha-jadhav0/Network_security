# Phishing Email Risk Prediction System Using Historical Email Behaviour & Machine Learning

A complete, production-grade **Full-Stack Network Security & Machine Learning Academic Capstone Application**.

This system detects whether incoming emails are legitimate or phishing threats, analyzes historical user email reception patterns, and applies predictive modeling to calculate future 24-hour phishing exposure risk scores.

---

## 🌟 Key Features

1. **Email Threat Classification Engine**:
   - Hybrid machine learning model using **TF-IDF Text Vectorization** + **Random Forest Classifier** (200 estimators).
   - Heuristic cybersecurity boost analyzing URL IP addresses, domain mismatches, urgent keywords, and uppercase ratios.

2. **AI-Powered Phishing Category Classifier (DistilBERT)**:
   - Hierarchical 2nd-stage NLP model fine-tuned on `distilbert-base-uncased`.
   - Categorizes phishing emails into 7 specific fraud threat types: `BANKING_FRAUD`, `TRANSACTION_FRAUD`, `LOTTERY_SCAM`, `JOB_FRAUD`, `ENTERTAINMENT_SCAM`, `CRYPTO_INVESTMENT_SCAM`, and `ACCOUNT_VERIFICATION_SCAM`.
   - Includes lazy loading, automatic dataset generation, and graceful fallback to `UNKNOWN`.

3. **Historical Behavioral Risk Scoring**:
   - Extracts 7 quantitative behavioral indicators over time.
   - Applies **Logistic Regression** to calculate 24-hour future phishing exposure risk probabilities ($0.0 - 1.0$).

4. **Email Header & Security Authentication Analysis**:
   - Parses raw MIME (`.eml`) emails and plain text.
   - Inspects SPF, DKIM, and DMARC authentication status, detecting domain spoofing and suspicious sender patterns.

5. **Cybersecurity Cyberpunk Dashboard**:
   - Built with **React.js**, **Tailwind CSS**, and **Recharts**.
   - Features 6 interactive graphs: 14-day attack volume, weekly risk exposure, 24-hour attack distribution, phishing vs. legitimate ratio, top suspicious domains, and fraud category distribution.

6. **Containerized Production Deployment**:
   - Multi-container architecture orchestrated via **Docker Compose** (FastAPI backend + React/Nginx frontend + SQLite auto-seeding database).

---

## 📐 System Architecture

```
[ Incoming Email / EML File ]
            │
            ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ FastAPI Security Gateway & Parser                           │
 ├─────────────────────────────────────────────────────────────┤
 │ • MIME Header Extraction (From, Reply-To, Received)         │
 │ • SPF / DKIM / DMARC Authentication Verification            │
 │ • Feature Engineering (Urgent Keywords, Domain Mismatch)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│  Stage 1: Binary Detector    │ │  Future Risk Prediction      │
│  (TF-IDF + Random Forest)    │ │  (Logistic Regression Model) │
│  Accuracy: 100% | F1: 1.00   │ │  Accuracy: 98.75% | F1: 0.99 │
└──────────────┬───────────────┘ └──────────────┬───────────────┘
               │ (If Phishing)                  │
               ▼                                │
┌──────────────────────────────┐                │
│  Stage 2: DistilBERT Model   │                │
│  7 Fraud Threat Categories   │                │
│  (Fine-Tuned HuggingFace NLP)│                │
└──────────────┬───────────────┘                │
               │                                │
               └────────────────┬───────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ SQLite Database (ORM: SQLAlchemy)                           │
 │ Stores: Users, Email Logs (with Categories), Daily Risk     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ React.js Cyber Intelligence Dashboard                       │
 │ Threat Badges, Recharts Time-Series, Category Analytics     │
 └─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology Used |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, Lucide Icons, Axios, React Router v6 |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy, PyJWT, Passlib / Bcrypt, Pydantic |
| **Machine Learning** | Scikit-Learn (RandomForestClassifier, LogisticRegression), Pandas, NumPy, Joblib, NLTK |
| **Database** | SQLite 3 (ORM schema configurable for PostgreSQL / MySQL) |
| **DevOps & Containers**| Docker, Docker Compose, Nginx (Alpine) |

---

## 📁 Repository Project Structure

```
Network_Security/
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   │   ├── train_classifier.py     # TF-IDF + Random Forest training script
│   │   │   ├── train_risk_model.py     # Logistic Regression behavioral risk trainer
│   │   │   ├── phishing_model.pkl      # Trained classification model artifact
│   │   │   └── risk_model.pkl          # Trained risk predictor model artifact
│   │   ├── routes/
│   │   │   ├── auth.py                 # JWT login, register, profile endpoints
│   │   │   ├── emails.py               # Email analysis, upload, history routes
│   │   │   ├── analytics.py            # Dashboard metrics & chart aggregations
│   │   │   └── prediction.py           # Future risk score endpoint
│   │   ├── services/
│   │   │   ├── email_parser.py         # MIME parsing & SPF/DKIM validation
│   │   │   ├── feature_engineering.py  # Urgent keyword & URL feature extraction
│   │   │   ├── phishing_detector.py    # Phishing inference service
│   │   │   └── risk_predictor.py       # Behavioral risk inference service
│   │   ├── database.py                 # SQLAlchemy engine & session setup
│   │   ├── main.py                     # FastAPI application & startup auto-seeding
│   │   ├── models.py                   # SQLAlchemy ORM models (User, Email, Risk)
│   │   └── schemas.py                  # Pydantic request & response schemas
│   ├── tests/
│   │   └── test_api.py                 # Pytest automated API suite (100% pass)
│   ├── Dockerfile                      # Backend container configuration
│   └── requirements.txt                # Python backend dependencies
├── dataset/
│   ├── generate_dataset.py             # Synthetic dataset generator script
│   ├── emails_dataset.csv              # Synthetic corpus of 500+ emails
│   └── user_history_dataset.csv        # Synthetic behavioral user records
├── frontend/
│   ├── src/
│   │   ├── components/                 # ThreatBadge, StatCard, Sidebar, Navbar
│   │   ├── context/                    # AuthContext (JWT session management)
│   │   ├── pages/                      # Dashboard, Upload, History, Analytics, Prediction
│   │   ├── services/                   # Axios API interceptor service
│   │   ├── App.jsx                     # Protected routing & main container
│   │   └── index.css                   # Cyberpunk dark mode styling
│   ├── Dockerfile                      # React Multi-stage Nginx container
│   ├── nginx.conf                      # Nginx reverse proxy configuration
│   ├── package.json                    # Frontend dependencies
│   ├── tailwind.config.js              # Tailwind custom theme configuration
│   └── vite.config.js                  # Vite build setup
├── docker-compose.yml                  # Unified multi-container deployment
├── LICENSE                             # MIT License
└── README.md                           # Technical documentation & Viva Q&A
```

---

## 🚀 Quickstart & Setup Guide

### Method 1: Using Docker Compose (Recommended)

1. Clone or navigate to the repository directory:
   ```bash
   cd Network_Security
   ```
2. Build and start the entire stack:
   ```bash
   docker compose up --build
   ```
3. Open your browser and navigate to:
   - **Frontend Security Dashboard**: `http://localhost:3000`
   - **Backend OpenAPI Documentation**: `http://localhost:8000/docs`

**Default Admin Credentials**:
- **Email**: `admin@example.com`
- **Password**: `Admin@123`

---

### Method 2: Manual Local Development Setup

#### 1. Backend Setup
```bash
# Navigate to project root
cd Network_Security

# Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Generate synthetic dataset and train machine learning models
python dataset/generate_dataset.py
python backend/app/ml/train_classifier.py
python backend/app/ml/train_risk_model.py

# Start FastAPI backend server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
# Open a new terminal tab and navigate to frontend directory
cd Network_Security/frontend

# Install Node dependencies
npm install

# Start Vite React development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 📊 Machine Learning Pipeline & Metrics

### 1. Phishing Text Classifier (`train_classifier.py`)
- **Algorithm**: `RandomForestClassifier` (n_estimators=200, max_depth=20) + `TfidfVectorizer` (max_features=3000, ngram_range=(1,2)).
- **Engineered Features**:
  - `url_count`: Total URLs embedded in body.
  - `has_ip_url`: Binary flag if URL uses raw IP address instead of domain.
  - `urgent_keyword_count`: Frequency of words like *verify, account, suspended, ssn, freeze, bank*.
  - `domain_mismatch`: Binary flag indicating sender header domain differs from claimed identity.
  - `uppercase_ratio`: Ratio of capital letters to total body length.
- **Evaluation Metrics**:
  - **Accuracy**: 100.0%
  - **Precision**: 100.0%
  - **Recall**: 100.0%
  - **F1 Score**: 1.000

### 2. Future Risk Prediction Model (`train_risk_model.py`)
- **Algorithm**: `LogisticRegression` (C=1.0, max_iter=1000).
- **Behavioral Feature Vector ($X$)**:
  1. `phishing_last_24h`: Count of phishing emails received in last 24 hours.
  2. `phishing_last_7d`: Count of phishing emails received in last 7 days.
  3. `unknown_sender_ratio`: Ratio of emails from unverified/new domains.
  4. `avg_url_count`: Average URLs per email received.
  5. `urgent_keyword_frequency`: Total urgent keywords encountered recently.
  6. `off_hours_email_ratio`: Ratio of emails received outside business hours (22:00 - 06:00).
  7. `suspicious_domain_count`: Count of flagged malicious sender domains.
- **Evaluation Metrics**:
  - **Accuracy**: 98.75%
  - **Precision**: 98.64%
  - **Recall**: 100.0%
  - **F1 Score**: 0.9932
  - **ROC-AUC**: 0.9987

---

## 🎓 Faculty Viva Voce Q&A Section (10 Detailed Technical Questions)

### Q1: Why did you combine ML classification with historical behavioral risk prediction instead of relying solely on text analysis?
**Answer**: Pure text analysis models evaluate emails in complete isolation. Modern spear-phishing attacks often use clean language without obvious spam words to bypass static text filters. By tracking user behavior over time (e.g., spike in unknown senders, off-hours reception, previous phishing exposure), our system predicts future risk exposure even if a single incoming message looks superficially legitimate.

### Q2: Why did you choose Random Forest over Deep Learning (e.g., BERT/LSTM) for email classification?
**Answer**: Random Forest provides superior performance on tabular/hybrid feature sets, offers fast inference times (crucial for real-time email gateways), requires significantly fewer computational resources, and prevents overfitting through ensemble bagging. Additionally, feature importance analysis in Random Forests allows transparent auditability for cybersecurity analysts.

### Q3: How does the system handle domain spoofing and header verification?
**Answer**: The backend `email_parser.py` extracts raw MIME headers (`From`, `Reply-To`, `Received`, `Authentication-Results`). It checks whether the display domain matches the actual sending SMTP domain and parses SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail), and DMARC (Domain-based Message Authentication) passes or failures.

### Q4: Explain the 7 features used in the future risk prediction model.
**Answer**:
1. `phishing_last_24h`: Indicates immediate ongoing targeted attack campaigns.
2. `phishing_last_7d`: Captures weekly baseline attack persistence.
3. `unknown_sender_ratio`: Measures user exposure to external unverified contacts.
4. `avg_url_count`: Higher URL density increases click-through attack vectors.
5. `urgent_keyword_frequency`: Indicates psychological pressure manipulation tactics.
6. `off_hours_email_ratio`: Threat actors frequently send phishing off-hours when IT security staff is offline.
7. `suspicious_domain_count`: Tracks repeated interactions with flagged domains.

### Q5: How is JWT authentication secured in the application?
**Answer**: User passwords are encrypted using `bcrypt` password hashing with cryptographic salt before database persistence. Upon successful authentication, the server generates a JSON Web Token (JWT) signed with `HS256` and an expiration timestamp. The frontend attaches this token via an HTTP `Authorization: Bearer <token>` header in an Axios interceptor.

### Q6: How does the auto-seeding mechanism work?
**Answer**: When FastAPI starts, `app/main.py` checks if database tables exist. If empty, it creates the database schema, seeds an initial administrator account (`admin@example.com`), and generates 25 realistic sample emails spanning 14 days so the analytics dashboard renders immediately upon first launch.

### Q7: What is the significance of the TF-IDF N-gram range `(1, 2)`?
**Answer**: Unigrams (single words) miss word context (e.g., "bank" vs. "bank account"). Using bi-grams `(1, 2)` allows TF-IDF to capture contextual phishing phrases such as "verify account", "click here", "password expired", and "action required", significantly increasing classification accuracy.

### Q8: How does Nginx function in the frontend container?
**Answer**: Nginx acts as a production HTTP web server serving compiled static React bundle files (`dist/`). It also serves as a reverse proxy, forwarding requests starting with `/api` directly to the FastAPI backend container (`http://backend:8000`), resolving CORS issues in production deployments.

### Q9: How are threat levels (LOW, MEDIUM, HIGH, CRITICAL) assigned?
**Answer**: Threat levels are assigned using a combined threshold function:
- **LOW**: Confidence $< 0.40$
- **MEDIUM**: $0.40 \le$ Confidence $< 0.70$
- **HIGH**: $0.70 \le$ Confidence $< 0.90$
- **CRITICAL**: Confidence $\ge 0.90$ or presence of raw IP URLs + missing SPF/DKIM headers.

### Q10: How can this system be scaled for an enterprise network?
**Answer**:
1. Replace SQLite with PostgreSQL or MySQL cluster.
2. Deploy FastAPI backend behind an API Gateway with Kubernetes auto-scaling.
3. Integrate real-time email protocol hooks (IMAP / SMTP / Microsoft Graph API webhooks) for active inbox scanning.
4. Implement continuous online learning to update ML weights as new phishing patterns emerge.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
