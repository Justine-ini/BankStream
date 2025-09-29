# secure_otp.py
import secrets
import string


def generate_otp(length: int = 6) -> str:
    """
    Generate a cryptographically secure numeric OTP of exact length (leading zeros allowed).
    Uses secrets.choice for cryptographic randomness.
    """
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))
