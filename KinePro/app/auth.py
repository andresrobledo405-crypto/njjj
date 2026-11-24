"""Autenticación: contraseñas con scrypt y sesión en cookie firmada (HMAC-SHA256)."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from .config import DATA_DIR

SESSION_COOKIE = "kinepro_session"
SESSION_SECONDS = 12 * 3600


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt_hex, digest_hex = stored.split("$")
        expected = hash_password(password, bytes.fromhex(salt_hex)).split("$")[2]
    except ValueError:
        return False
    return hmac.compare_digest(expected, digest_hex)


def _secret() -> bytes:
    env = os.getenv("KINEPRO_SECRET")
    if env:
        return env.encode()
    path = DATA_DIR / ".secret"
    if not path.exists():
        path.write_text(secrets.token_hex(32))
        try:
            path.chmod(0o600)
        except OSError:
            pass
    return path.read_text().strip().encode()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def make_token(user: dict) -> str:
    payload = _b64(json.dumps({"id": user["id"], "u": user["username"], "r": user["role"], "exp": int(time.time()) + SESSION_SECONDS}).encode())
    return f"{payload}.{_b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())}"


def read_token(token: str | None) -> dict | None:
    if not token or "." not in token:
        return None
    payload, signature = token.rsplit(".", 1)
    expected = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except ValueError:
        return None
    return data if data.get("exp", 0) > time.time() else None


class LoginThrottle:
    """Bloquea 5 minutos tras 5 intentos fallidos por usuario+IP."""

    def __init__(self, limit: int = 5, window: int = 300):
        self.limit, self.window, self.fails = limit, window, {}

    def _recent(self, key):
        now = time.time()
        self.fails[key] = [t for t in self.fails.get(key, []) if now - t < self.window]
        return self.fails[key]

    def blocked(self, key) -> bool:
        return len(self._recent(key)) >= self.limit

    def fail(self, key) -> None:
        self._recent(key).append(time.time())

    def reset(self, key) -> None:
        self.fails.pop(key, None)


throttle = LoginThrottle()
