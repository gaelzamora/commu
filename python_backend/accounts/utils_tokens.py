import os, pyotp
from datetime import timedelta, datetime, timezone
from rest_framework_simplejwt.tokens import AccessToken
from cryptography.fernet import Fernet

FERNET = Fernet(os.environ["FERNET_KEY"].encode())

def make_registration_token(email: str, ttl_minutes=15) -> str:
    t = AccessToken()
    t.set_exp(from_time=datetime.now(timezone.utc), lifetime=timedelta(minutes=ttl_minutes))
    t["purpose"] = "register"
    t["email"] = email.lower()
    return str(t)

def validate_registration_token(token_obj) -> str:
    if token_obj.get("purpose") != "register":
        raise ValueError("invalid purpose")
    email = token_obj.get("email")
    if not email: raise ValueError("email missing")
    return email

# MFA (TOTP)
def new_totp_secret() -> str:
    return pyotp.random_base32()

def encrypt_secret(secret: str) -> bytes:
    return FERNET.encrypt(secret.encode())

def decrypt_secret(enc: bytes) -> str:
    return FERNET.decrypt(enc).decode()


def totp_uri(secret: str, user_label: str, issuer: str="Commu Backend"):
    return pyotp.TOTP(secret).provisioning_uri(name=user_label, issuer_name=issuer)

def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1) 