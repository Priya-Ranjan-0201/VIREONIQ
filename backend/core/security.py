import os
import uuid
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Dict

from jose import jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from core.config import settings

# Argon2id context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def _ensure_keys_exist():
    if not os.path.exists(".secrets"):
        os.makedirs(".secrets")
    
    if not os.path.exists(settings.PRIVATE_KEY_PATH) or not os.path.exists(settings.PUBLIC_KEY_PATH):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        
        with open(settings.PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        with open(settings.PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

_ensure_keys_exist()

with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
    PRIVATE_KEY = key_file.read()

with open(settings.PUBLIC_KEY_PATH, "rb") as key_file:
    PUBLIC_KEY = key_file.read()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its Argon2id hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using the Argon2id hashing scheme."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], jti: str, expires_delta: timedelta = None) -> str:
    """Create an RS256 signed JWT access token for a subject."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "jti": jti, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], jti: str, expires_delta: timedelta = None) -> str:
    """Create an RS256 signed JWT refresh token for a subject."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode = {"exp": expire, "sub": str(subject), "jti": jti, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate an RS256 signed JWT token using the public key."""
    return jwt.decode(token, PUBLIC_KEY, algorithms=[settings.JWT_ALGORITHM])

def check_prompt_injection(text: str) -> bool:
    """
    Performs comprehensive security screening on user-provided strings.
    Checks for:
    1. Multi-vector Prompt Injection & LLM jailbreaks (DAN, Developer Mode, Roleplay, Instruction Ignoral)
    2. SQL Injection signatures (UNION SELECT, tautologies, hex representations)
    3. XSS vectors (script tags, onerror/onload handlers, javascript: pseudo-protocol)
    4. Path Traversal & System File Access attempts (etc/passwd, win.ini, directory navigation)
    5. Base64 Obfuscated Command signatures
    """
    if not text:
        return False
        
    normalized = text.lower().strip()
    
    # 1. Advanced Prompt Injection & Jailbreak Heuristics
    injection_patterns = [
        "ignore previous instructions",
        "ignore the instructions",
        "ignore all instructions",
        "system prompt",
        "you are now a",
        "override the above",
        "override the instructions",
        "bypass the filter",
        "jailbreak",
        "do not follow",
        "forget what i said",
        "forget the previous",
        "disregard",
        "assistant mode",
        "developer mode",
        "do anything now",
        "acting as a",
        "roleplay as",
        "hypothetical scenario where",
        "simulate a scenario",
        "you are unrestricted",
        "rules are suspended",
        "dan mode",
        "dan 6.0",
        "jailbroken",
        "ignore any filters",
        "bypass safety",
        "[system:",
        "[user:",
        "[assistant:",
        "role: system",
        "role: user",
        "role: assistant"
    ]
    
    for pattern in injection_patterns:
        if pattern in normalized:
            return True
            
    # 2. SQL Injection Signatures
    sql_patterns = [
        r"\bor\b\s+['\"`]?\d+['\"`]?\s*=\s*['\"`]?\d+['\"`]?", # tautology
        r"\bunion\b\s+(all\s+)?\bselect\b",                     # union select
        r"\bselect\b.*\bfrom\b\s+users",                        # select from users
        r"\bdrop\b\s+table\b",                                  # drop table
        r"\binsert\b\s+into\b",                                 # insert into
        r"\bdelete\b\s+from\b",                                 # delete from
        r"--",                                                  # comment
        r"/\*.*\*/"                                             # block comment
    ]
    for pattern in sql_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
            
    # 3. Cross-Site Scripting (XSS) Signatures
    xss_patterns = [
        r"<script\b[^>]*>",
        r"javascript\s*:",
        r"\bonerror\s*=",
        r"\bonload\s*=",
        r"\bonmouseover\s*=",
        r"\balert\s*\("
    ]
    for pattern in xss_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
            
    # 4. Path Traversal & System Access Signatures
    traversal_patterns = [
        r"\.\./",
        r"\.\.\\",
        r"/etc/passwd",
        r"/etc/shadow",
        r"win\.ini",
        r"boot\.ini",
        r"/windows/system32"
    ]
    for pattern in traversal_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
            
    # 5. Base64 Obfuscated Command Signatures
    base64_pattern = r"\b[a-zA-Z0-9+/]{20,}(?:==|=)?"
    if re.search(base64_pattern, text):
        import base64
        matches = re.findall(base64_pattern, text)
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode("utf-8", errors="ignore").lower()
                for pattern in ["exploit", "exec", "system", "cmd", "ignore", "passwd", "script"]:
                    if pattern in decoded:
                        return True
            except Exception:
                pass

    return False


