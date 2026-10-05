from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Authentication Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None

# Email Analysis Schemas
class SenderDomainAnalysis(BaseModel):
    domain: str
    is_suspicious: bool
    is_mismatched: bool = False
    has_ip_url: bool = False

class EmailAnalyzeRequest(BaseModel):
    sender: str = Field(..., example="security-update@paypa1-alert.com")
    subject: str = Field(..., example="Verify your account immediately")
    body: str = Field(..., example="Click the link below to avoid suspension.")
    headers_text: Optional[str] = None

class HeaderAnalysisResult(BaseModel):
    from_header: Optional[str] = None
    reply_to: Optional[str] = None
    return_path: Optional[str] = None
    received_chain: List[str] = []
    has_spf: bool = False
    has_dkim: bool = False
    has_dmarc: bool = False
    auth_warning: str = ""

class EmailAnalyzeResponse(BaseModel):
    id: Optional[int] = None
    sender: str
    subject: str
    is_phishing: bool
    confidence: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    phishing_category: Optional[str] = None
    category_confidence: Optional[float] = None
    suspicious_keywords: List[str]
    url_count: int
    sender_domain_analysis: SenderDomainAnalysis
    header_analysis: Optional[HeaderAnalysisResult] = None
    received_at: Optional[datetime] = None

class EmailHistoryItem(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime
    is_phishing: bool
    confidence: float
    risk_level: str
    phishing_category: Optional[str] = None
    category_confidence: Optional[float] = None
    url_count: int
    suspicious_keywords: List[str]

    class Config:
        from_attributes = True

# Analytics & Dashboard Schemas
class StatCardData(BaseModel):
    total_emails: int
    phishing_count: int
    legitimate_count: int
    current_risk_score: float
    current_risk_level: str

class TrendPoint(BaseModel):
    date: str
    phishing: int
    legitimate: int

class WeeklyRiskPoint(BaseModel):
    date: str
    risk_probability: float

class SuspiciousDomainItem(BaseModel):
    domain: str
    count: int

class KeywordCountItem(BaseModel):
    keyword: str
    count: int

class HourlyAttackItem(BaseModel):
    hour: int
    count: int

class CategoryCountItem(BaseModel):
    category: str
    count: int

class DashboardAnalyticsResponse(BaseModel):
    stats: StatCardData
    daily_trend: List[TrendPoint]
    weekly_risk: List[WeeklyRiskPoint]
    top_suspicious_domains: List[SuspiciousDomainItem]
    phishing_vs_legit: Dict[str, int]
    hourly_distribution: List[HourlyAttackItem]
    recent_suspicious: List[EmailHistoryItem]
    common_keywords: List[KeywordCountItem]
    category_distribution: List[CategoryCountItem] = []

# Future Risk Prediction Schema
class FutureRiskResponse(BaseModel):
    user_id: int
    future_risk_probability: float
    predicted_risk: str # LOW, MEDIUM, HIGH
    features_used: Dict[str, Any]
    recommendation: str
