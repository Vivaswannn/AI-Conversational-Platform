import os
import pytest
from app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear lru_cache before and after each test to prevent bleed-through."""
    get_settings.cache_clear()
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")
    yield
    get_settings.cache_clear()


def test_settings_loads_defaults():
    s = get_settings()
    assert s.ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert s.OPENAI_MODEL == "gpt-4o"


def test_settings_is_cached():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_app_name_and_version():
    s = get_settings()
    assert s.APP_NAME == "AI Conversational Support Platform"
    assert s.APP_VERSION == "0.1.0"
