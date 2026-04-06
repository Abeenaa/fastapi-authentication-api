import base64
import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 390000
SALT_BYTES = 16


def _pbkdf2_hash(plain_password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )


def hash_password(plain_password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _pbkdf2_hash(plain_password, salt, ITERATIONS)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{ALGORITHM}${ITERATIONS}${salt_b64}${digest_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, digest_b64 = hashed_password.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_str)
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected_digest = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual_digest = _pbkdf2_hash(plain_password, salt, iterations)
    return hmac.compare_digest(actual_digest, expected_digest)
