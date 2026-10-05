import re
from typing import Dict, Any, List, Set

URGENT_KEYWORDS = [
    "verify", "suspend", "password", "otp", "bank", "update", "billing",
    "action required", "security alert", "unauthorized", "locked", "expire",
    "immediate", "termination", "ssn", "debit card", "crypto", "refund",
    "urgent", "breach", "purged", "overdue", "due today", "confirm"
]

DANGEROUS_EXTENSIONS = {".exe", ".bat", ".scr", ".js", ".vbs", ".cmd", ".pif", ".application", ".ps1", ".jar", ".iso"}

IP_ADDRESS_REGEX = re.compile(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE)

class FeatureEngineeringService:
    @staticmethod
    def extract_features(sender: str, subject: str, body: str, urls: List[str], attachments: List[str] = None, reply_to: str = "") -> Dict[str, Any]:
        """
        Extract all quantitative security features for phishing detection.
        """
        attachments = attachments or []
        combined_text = f"{subject} {body}".lower()
        
        # 1. URL count
        url_count = len(urls)
        
        # 2. IP Address URL detection
        has_ip_url = any(bool(IP_ADDRESS_REGEX.search(u)) for u in urls)
        
        # 3. Urgent words detected
        found_urgent_words = []
        for word in URGENT_KEYWORDS:
            if word in combined_text:
                found_urgent_words.append(word)
        found_urgent_words = list(set(found_urgent_words))
        
        # 4. Sender domain mismatch / display name spoofing
        sender_domain = ""
        if "@" in sender:
            # handle 'Display Name <email@domain.com>'
            clean_email = re.findall(r'[\w\.-]+@[\w\.-]+', sender)
            if clean_email:
                sender_domain = clean_email[0].split("@")[-1].lower()
            else:
                sender_domain = sender.split("@")[-1].lower()
                
        reply_domain = ""
        if reply_to and "@" in reply_to:
            clean_reply = re.findall(r'[\w\.-]+@[\w\.-]+', reply_to)
            if clean_reply:
                reply_domain = clean_reply[0].split("@")[-1].lower()
        
        sender_domain_mismatch = False
        if reply_domain and sender_domain and reply_domain != sender_domain:
            sender_domain_mismatch = True
            
        # Also flag suspicious TLDs (.xyz, .top, .info, .click, .tech, .site, .online)
        suspicious_tlds = [".xyz", ".top", ".info", ".click", ".tech", ".site", ".online"]
        is_suspicious_domain = any(sender_domain.endswith(tld) for tld in suspicious_tlds)
        
        # 5. Dangerous attachment extension
        attachment_exe = False
        for att in attachments:
            att_lower = att.lower()
            if any(att_lower.endswith(ext) for ext in DANGEROUS_EXTENSIONS):
                attachment_exe = True
                break

        # 6. Uppercase ratio
        total_letters = sum(1 for c in body if c.isalpha())
        uppercase_letters = sum(1 for c in body if c.isupper())
        uppercase_ratio = (uppercase_letters / total_letters) if total_letters > 0 else 0.0
        
        # 7. Special character ratio
        total_chars = len(body)
        special_chars = sum(1 for c in body if c in "!@#$%^&*()[]{}=+;:'\"<>,?/")
        special_char_ratio = (special_chars / total_chars) if total_chars > 0 else 0.0

        return {
            "url_count": url_count,
            "has_ip_address_url": has_ip_url,
            "urgent_words": found_urgent_words,
            "urgent_word_count": len(found_urgent_words),
            "sender_domain": sender_domain,
            "sender_domain_mismatch": sender_domain_mismatch,
            "is_suspicious_domain": is_suspicious_domain,
            "attachment_exe": attachment_exe,
            "uppercase_ratio": round(uppercase_ratio, 4),
            "special_char_ratio": round(special_char_ratio, 4)
        }
