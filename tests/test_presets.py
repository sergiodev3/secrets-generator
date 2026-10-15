import pytest

from secrets_generator.core import (
    MIN_BYTES,
    PRESETS,
    SecretFormat,
    generate_secret,
    is_valid_env_name,
)


def test_presets_cover_common_secrets():
    by_label = {preset.label: preset for preset in PRESETS}
    assert by_label["JWT secret (HS256)"].name == "JWT_SECRET"
    assert by_label["JWT secret (HS256)"].num_bytes == 32
    assert by_label["JWT secret (HS512)"].num_bytes == 64
    assert by_label["Session secret"].name == "SESSION_SECRET"
    assert by_label["API key"].fmt is SecretFormat.ALNUM


@pytest.mark.parametrize("preset", PRESETS, ids=lambda preset: preset.label)
def test_preset_is_valid(preset):
    assert is_valid_env_name(preset.name)
    assert preset.num_bytes >= MIN_BYTES
    assert generate_secret(preset.num_bytes, preset.fmt)


def test_presets_are_immutable():
    with pytest.raises(AttributeError):
        PRESETS[0].num_bytes = 8
