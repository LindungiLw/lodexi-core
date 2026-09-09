import os
import pytest
from fastapi.testclient import TestClient

# Force in-memory settings for test suite
os.environ["QDRANT_MODE"] = "memory"
os.environ["EMBEDDING_PROVIDER"] = "fast-mock"
os.environ["LLM_PROVIDER"] = "mock"

from src.config import settings
settings.QDRANT_MODE = "memory"
settings.EMBEDDING_PROVIDER = "fast-mock"
settings.LLM_PROVIDER = "mock"

from src.main import app

KEY_JIULIBRARY = "key_jiulibrary_secret_123"
KEY_STAFFPORTAL = "key_staffportal_secret_456"


@pytest.fixture(scope="session")
def client():
    """Reusable FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers_jiulibrary():
    """Headers for tenant jiulibrary."""
    return {"X-API-Key": KEY_JIULIBRARY}


@pytest.fixture
def headers_staffportal():
    """Headers for tenant staff_portal."""
    return {"X-API-Key": KEY_STAFFPORTAL}
