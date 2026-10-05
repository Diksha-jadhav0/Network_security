import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    emails = relationship("Email", back_populates="owner", cascade="all, delete-orphan")
    daily_stats = relationship("DailyRiskStats", back_populates="owner", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_phishing = Column(Boolean, nullable=False, default=False)
    confidence = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(20), nullable=False, default="LOW")
    phishing_category = Column(String, nullable=True)
    category_confidence = Column(Float, default=0.0)
    url_count = Column(Integer, nullable=False, default=0)
    suspicious_keywords = Column(Text, nullable=True) # Stored as JSON string or comma-separated
    headers_json = Column(Text, nullable=True) # Stored JSON of parsed headers & auth
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="emails")

class DailyRiskStats(Base):
    __tablename__ = "daily_risk_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String(10), nullable=False, index=True) # YYYY-MM-DD
    phishing_last_24h = Column(Integer, default=0)
    phishing_last_7d = Column(Integer, default=0)
    unknown_sender_ratio = Column(Float, default=0.0)
    avg_url_count = Column(Float, default=0.0)
    future_risk_probability = Column(Float, default=0.0)
    predicted_risk = Column(String(20), default="LOW")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="daily_stats")
