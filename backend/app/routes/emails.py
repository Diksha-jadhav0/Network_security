import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Email
from ..schemas import EmailAnalyzeRequest, EmailAnalyzeResponse, EmailHistoryItem, HeaderAnalysisResult
from .auth import get_current_user
from ..services.email_parser import EmailParserService
from ..services.phishing_detector import PhishingDetectorService
from ..services.category_classifier import classify_category

router = APIRouter(prefix="/api/emails", tags=["Email Threat Processing"])

@router.post("/analyze", response_model=EmailAnalyzeResponse)
def analyze_email_json(
    payload: EmailAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze JSON input email content for phishing indicators, store record, and return risk assessment.
    """
    parsed = EmailParserService.parse_plain_text(
        raw_text=payload.body,
        sender=payload.sender,
        subject=payload.subject
    )
    
    detection = PhishingDetectorService.analyze_email(
        sender=parsed["sender"],
        subject=parsed["subject"],
        body=parsed["body"],
        urls=parsed["urls"]
    )
    
    full_text = f"{parsed['subject']} {parsed['body']}"
    if detection["is_phishing"]:
        cat_res = classify_category(full_text)
    else:
        cat_res = {"category": "LEGITIMATE", "confidence": 1.0}

    # Store email record in DB
    db_email = Email(
        user_id=current_user.id,
        sender=parsed["sender"],
        subject=parsed["subject"],
        body=parsed["body"],
        received_at=datetime.utcnow(),
        is_phishing=detection["is_phishing"],
        confidence=detection["confidence"],
        risk_level=detection["risk_level"],
        phishing_category=cat_res["category"],
        category_confidence=cat_res["confidence"],
        url_count=detection["url_count"],
        suspicious_keywords=json.dumps(detection["suspicious_keywords"]),
        headers_json=json.dumps({
            "has_spf": parsed["has_spf"],
            "has_dkim": parsed["has_dkim"],
            "has_dmarc": parsed["has_dmarc"],
            "auth_warning": parsed["auth_warning"]
        })
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    
    return EmailAnalyzeResponse(
        id=db_email.id,
        sender=db_email.sender,
        subject=db_email.subject,
        is_phishing=db_email.is_phishing,
        confidence=db_email.confidence,
        risk_level=db_email.risk_level,
        phishing_category=db_email.phishing_category,
        category_confidence=db_email.category_confidence,
        suspicious_keywords=detection["suspicious_keywords"],
        url_count=detection["url_count"],
        sender_domain_analysis=detection["sender_domain_analysis"],
        header_analysis=HeaderAnalysisResult(
            from_header=parsed["sender"],
            reply_to=parsed["reply_to"],
            return_path=parsed["return_path"],
            received_chain=parsed["received_chain"],
            has_spf=parsed["has_spf"],
            has_dkim=parsed["has_dkim"],
            has_dmarc=parsed["has_dmarc"],
            auth_warning=parsed["auth_warning"]
        ),
        received_at=db_email.received_at
    )

@router.post("/upload", response_model=EmailAnalyzeResponse)
async def upload_email_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse .eml or .txt email file, perform security extraction and ML classification.
    """
    filename = file.filename.lower()
    content_bytes = await file.read()
    
    if filename.endswith(".eml"):
        parsed = EmailParserService.parse_eml_content(content_bytes)
    else:
        text_content = content_bytes.decode("utf-8", errors="ignore")
        parsed = EmailParserService.parse_plain_text(text_content)

    detection = PhishingDetectorService.analyze_email(
        sender=parsed["sender"],
        subject=parsed["subject"],
        body=parsed["body"],
        urls=parsed["urls"],
        attachments=parsed["attachments"],
        reply_to=parsed["reply_to"]
    )
    
    full_text = f"{parsed['subject']} {parsed['body']}"
    if detection["is_phishing"]:
        cat_res = classify_category(full_text)
    else:
        cat_res = {"category": "LEGITIMATE", "confidence": 1.0}

    db_email = Email(
        user_id=current_user.id,
        sender=parsed["sender"],
        subject=parsed["subject"],
        body=parsed["body"],
        received_at=datetime.utcnow(),
        is_phishing=detection["is_phishing"],
        confidence=detection["confidence"],
        risk_level=detection["risk_level"],
        phishing_category=cat_res["category"],
        category_confidence=cat_res["confidence"],
        url_count=detection["url_count"],
        suspicious_keywords=json.dumps(detection["suspicious_keywords"]),
        headers_json=json.dumps({
            "has_spf": parsed["has_spf"],
            "has_dkim": parsed["has_dkim"],
            "has_dmarc": parsed["has_dmarc"],
            "auth_warning": parsed["auth_warning"]
        })
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)

    return EmailAnalyzeResponse(
        id=db_email.id,
        sender=db_email.sender,
        subject=db_email.subject,
        is_phishing=db_email.is_phishing,
        confidence=db_email.confidence,
        risk_level=db_email.risk_level,
        phishing_category=db_email.phishing_category,
        category_confidence=db_email.category_confidence,
        suspicious_keywords=detection["suspicious_keywords"],
        url_count=detection["url_count"],
        sender_domain_analysis=detection["sender_domain_analysis"],
        header_analysis=HeaderAnalysisResult(
            from_header=parsed["sender"],
            reply_to=parsed["reply_to"],
            return_path=parsed["return_path"],
            received_chain=parsed["received_chain"],
            has_spf=parsed["has_spf"],
            has_dkim=parsed["has_dkim"],
            has_dmarc=parsed["has_dmarc"],
            auth_warning=parsed["auth_warning"]
        ),
        received_at=db_email.received_at
    )

@router.get("/history", response_model=List[EmailHistoryItem])
def get_email_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve historical analyzed emails for current user.
    """
    emails = db.query(Email).filter(Email.user_id == current_user.id).order_by(Email.received_at.desc()).limit(limit).all()
    
    result = []
    for email in emails:
        kw_list = []
        if email.suspicious_keywords:
            try:
                kw_list = json.loads(email.suspicious_keywords) if email.suspicious_keywords.startswith("[") else [k.strip() for k in email.suspicious_keywords.split(",")]
            except Exception:
                kw_list = []
                
        result.append(EmailHistoryItem(
            id=email.id,
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            received_at=email.received_at,
            is_phishing=email.is_phishing,
            confidence=email.confidence,
            risk_level=email.risk_level,
            phishing_category=(
                email.phishing_category
                if email.phishing_category
                else ("LEGITIMATE" if not email.is_phishing else "UNKNOWN")
            ),
            category_confidence=(
                email.category_confidence
                if email.category_confidence is not None
                else (1.0 if not email.is_phishing else 0.0)
            ),
            url_count=email.url_count,
            suspicious_keywords=kw_list
        ))
    return result


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email_rec = db.query(Email).filter(Email.id == email_id, Email.user_id == current_user.id).first()
    if not email_rec:
        raise HTTPException(status_code=404, detail="Email record not found")
    db.delete(email_rec)
    db.commit()
    return None
