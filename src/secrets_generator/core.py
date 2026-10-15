"""Secret generation backed by the OS CSPRNG (``secrets`` module)."""

import base64
import math
import re
import secrets
import string
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
