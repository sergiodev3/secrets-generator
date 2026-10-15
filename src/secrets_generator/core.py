"""Secret generation backed by the OS CSPRNG (``secrets`` module)."""

import base64
import math
import re
import secrets
import string
from dataclasses import dataclass
from enum import StrEnum
from importlib.metadata import PackageNotFoundError, version

DIST_NAME = "secrets-generator"
MIN_BYTES = 16
DEFAULT_BYTES = 32

_ALNUM_ALPHABET = string.ascii_letters + string.digits
_ENV_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class SecretFormat(StrEnum):
    BASE64URL = "base64url"
    BASE64 = "base64"
    HEX = "hex"
    ALNUM = "alnum"


@dataclass(frozen=True)
class Preset:
    """Ready-made settings for a common kind of secret."""

    label: str
    name: str
    num_bytes: int
    fmt: SecretFormat
    description: str


PRESETS: tuple[Preset, ...] = (
    Preset("JWT secret (HS256)", "JWT_SECRET", 32, SecretFormat.BASE64URL, "256 bits, base64url"),
    Preset("JWT secret (HS512)", "JWT_SECRET", 64, SecretFormat.BASE64URL, "512 bits, base64url"),
    Preset("Session secret", "SESSION_SECRET", 32, SecretFormat.BASE64URL, "256 bits, base64url"),
    Preset("API key", "API_KEY", 32, SecretFormat.ALNUM, "256 bits, letters and digits"),
)


def generate_secret(num_bytes: int = DEFAULT_BYTES, fmt: SecretFormat = SecretFormat.BASE64URL) -> str:
    """Return a secret with at least ``num_bytes * 8`` bits of entropy."""
    if num_bytes < MIN_BYTES:
        raise ValueError(f"num_bytes must be at least {MIN_BYTES}, got {num_bytes}")

    match fmt:
        case SecretFormat.BASE64URL:
            return secrets.token_urlsafe(num_bytes)
        case SecretFormat.BASE64:
            return base64.b64encode(secrets.token_bytes(num_bytes)).decode("ascii")
        case SecretFormat.HEX:
            return secrets.token_hex(num_bytes)
        case SecretFormat.ALNUM:
            length = math.ceil(num_bytes * 8 / math.log2(len(_ALNUM_ALPHABET)))
            return "".join(secrets.choice(_ALNUM_ALPHABET) for _ in range(length))


def is_valid_env_name(name: str) -> bool:
    return _ENV_NAME_PATTERN.fullmatch(name) is not None


def package_version() -> str:
    """Return the installed distribution version, or a placeholder when not installed."""
    try:
        return version(DIST_NAME)
    except PackageNotFoundError:
        return "0.0.0+unknown"
