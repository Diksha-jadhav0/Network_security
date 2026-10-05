import re
import email
from email import policy
from email.parser import Parser as MIMEParser
from typing import Dict, Any, List, Tuple

DANGEROUS_EXTENSIONS = {".exe", ".bat", ".scr", ".js", ".vbs", ".cmd", ".pif", ".application", ".ps1", ".jar", ".iso"}

URL_REGEX = re.compile(
    r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s"\']*)?|http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/[^\s"\']*)?',
    re.IGNORECASE
)

IP_URL_REGEX = re.compile(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE)

class EmailParserService:
    @staticmethod
    def parse_eml_content(content_bytes: bytes) -> Dict[str, Any]:
        """
        Parse raw .eml file byte content.
        Extract sender, subject, body, headers, URLs, attachments, authentication headers.
        """
        msg = email.message_from_bytes(content_bytes, policy=policy.default)
        
        sender = str(msg.get("From", ""))
        subject = str(msg.get("Subject", ""))
        reply_to = str(msg.get("Reply-To", ""))
        return_path = str(msg.get("Return-Path", ""))
        
        received_chain = msg.get_all("Received") or []
        received_headers = [str(r) for r in received_chain]
        
        body_text = ""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
                elif content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body_text += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                    except Exception:
                        pass
                elif content_type == "text/html" and not body_text and "attachment" not in content_disposition:
                    try:
                        html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        # Strip HTML tags
                        body_text += re.sub(r'<[^>]+>', ' ', html_content)
                    except Exception:
                        pass
        else:
            try:
                body_text = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
            except Exception:
                body_text = str(msg.get_payload())

        # Clean body text whitespace
        body_text = re.sub(r'\s+', ' ', body_text).strip()
        
        # Check SPF / DKIM / DMARC authentication headers
        auth_results = str(msg.get("Authentication-Results", "")).lower()
        received_spf = str(msg.get("Received-SPF", "")).lower()
        dkim_sig = msg.get("DKIM-Signature", None)
        
        has_spf = ("pass" in auth_results and "spf" in auth_results) or ("pass" in received_spf)
        has_dkim = dkim_sig is not None or ("pass" in auth_results and "dkim" in auth_results)
        has_dmarc = "dmarc=pass" in auth_results
        
        auth_warning = ""
        if not (has_spf or has_dkim):
            auth_warning = "WARNING: Email lacks valid SPF or DKIM authentication records!"
        elif not has_dmarc:
            auth_warning = "NOTICE: DMARC policy validation record is missing."

        urls = URL_REGEX.findall(body_text)
        
        return {
            "sender": sender,
            "subject": subject,
            "body": body_text,
            "reply_to": reply_to,
            "return_path": return_path,
            "received_chain": received_headers,
            "attachments": attachments,
            "urls": urls,
            "has_spf": has_spf,
            "has_dkim": has_dkim,
            "has_dmarc": has_dmarc,
            "auth_warning": auth_warning
        }

    @staticmethod
    def parse_plain_text(raw_text: str, sender: str = "", subject: str = "") -> Dict[str, Any]:
        """
        Parse raw plain text email input or .txt file content.
        """
        # If subject/sender embedded in text headers (e.g. From: ..., Subject: ...)
        lines = raw_text.splitlines()
        extracted_sender = sender
        extracted_subject = subject
        body_lines = []
        
        in_header = True
        for line in lines:
            if in_header and ":" in line:
                key, val = line.split(":", 1)
                key_lower = key.strip().lower()
                if key_lower == "from" and not extracted_sender:
                    extracted_sender = val.strip()
                elif key_lower == "subject" and not extracted_subject:
                    extracted_subject = val.strip()
                elif line.strip() == "":
                    in_header = False
                else:
                    body_lines.append(line)
            else:
                body_lines.append(line)

        body_text = "\n".join(body_lines).strip()
        if not extracted_sender:
            extracted_sender = "unknown@external-source.com"
        if not extracted_subject:
            extracted_subject = "No Subject"

        urls = URL_REGEX.findall(body_text) + URL_REGEX.findall(raw_text)
        urls = list(set(urls))
        
        return {
            "sender": extracted_sender,
            "subject": extracted_subject,
            "body": body_text if body_text else raw_text,
            "reply_to": "",
            "return_path": "",
            "received_chain": [],
            "attachments": [],
            "urls": urls,
            "has_spf": False,
            "has_dkim": False,
            "has_dmarc": False,
            "auth_warning": "Plain text input lacks email headers; SPF/DKIM authentication missing."
        }
