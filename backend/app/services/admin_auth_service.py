import base64
import hashlib
import hmac
import json
import time

from fastapi import Header, HTTPException

from app.config import ADMIN_PASSWORD, ADMIN_SECRET, ADMIN_USERNAME


TOKEN_TTL_SECONDS = 60 * 60 * 8


def encode_base64url(value):
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def decode_base64url(value):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("utf-8"))


def sign_payload(payload):
    return hmac.new(
        ADMIN_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_admin_token(username):
    payload = encode_base64url(
        json.dumps(
            {
                "sub": username,
                "exp": int(time.time()) + TOKEN_TTL_SECONDS,
            },
            separators=(",", ":"),
        ).encode("utf-8")
    )
    signature = sign_payload(payload)

    return f"{payload}.{signature}"


def verify_admin_credentials(username, password):
    return hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(
        password,
        ADMIN_PASSWORD,
    )


def verify_admin_token(token):
    try:
        payload, signature = token.split(".", 1)
        expected_signature = sign_payload(payload)

        if not hmac.compare_digest(signature, expected_signature):
            return False

        data = json.loads(decode_base64url(payload).decode("utf-8"))

        return (
            data.get("sub") == ADMIN_USERNAME
            and int(data.get("exp", 0)) >= int(time.time())
        )
    except (ValueError, TypeError, json.JSONDecodeError):
        return False


def require_admin(authorization: str = Header("")):
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not verify_admin_token(token):
        raise HTTPException(
            status_code=401,
            detail="Akses admin diperlukan. Silakan login sebagai admin.",
        )

    return True
