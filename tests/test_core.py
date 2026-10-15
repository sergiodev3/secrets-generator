import math
import re
import string

import pytest

from secrets_generator.core import (
    MIN_BYTES,
    SecretFormat,
    generate_secret,
    is_valid_env_name,
)


def test_hex_length_is_two_chars_per_byte():
    assert len(generate_secret(32, SecretFormat.HEX)) == 64


def test_hex_only_contains_hex_chars():
    assert set(generate_secret(32, SecretFormat.HEX)) <= set(string.hexdigits.lower())


def test_base64url_is_url_safe_and_unpadded():
    value = generate_secret(32, SecretFormat.BASE64URL)
    assert re.fullmatch(r"[A-Za-z0-9_-]+", value)
    assert len(value) == 43


def test_base64_is_standard_encoding():
    value = generate_secret(32, SecretFormat.BASE64)
    assert re.fullmatch(r"[A-Za-z0-9+/]+=*", value)
    assert len(value) == 44


def test_alnum_has_at_least_requested_entropy():
    value = generate_secret(32, SecretFormat.ALNUM)
    assert value.isalnum()
    assert len(value) * math.log2(62) >= 32 * 8


def test_values_are_not_repeated():
    values = {generate_secret(32, SecretFormat.BASE64URL) for _ in range(100)}
    assert len(values) == 100


def test_rejects_too_few_bytes():
    with pytest.raises(ValueError):
        generate_secret(MIN_BYTES - 1, SecretFormat.HEX)


@pytest.mark.parametrize("name", ["JWT_SECRET", "_PRIVATE", "key1"])
def test_valid_env_names(name):
    assert is_valid_env_name(name)


@pytest.mark.parametrize("name", ["1KEY", "MY-KEY", "MY KEY", "", "KEY="])
def test_invalid_env_names(name):
    assert not is_valid_env_name(name)
