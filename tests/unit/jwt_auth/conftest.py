"""
Pytest configuration for JWT authentication tests.
"""

import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from django.conf import settings
from jwt.algorithms import ECAlgorithm

# Generate ES256 test keys for JWT authentication
_test_private_key = ec.generate_private_key(ec.SECP256R1())
_test_public_key = _test_private_key.public_key()

# Serialize private key to PEM format
TEST_ES256_PRIVATE_KEY = _test_private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)


@pytest.fixture(autouse=True)
def mock_es256_key(request, monkeypatch):
    """
    Automatically mock the ES256 public key for JWT tests.
    This allows tests to generate and verify JWTs with test keys.

    Skips mocking for integration tests (marked with @pytest.mark.integration).
    """

    # Create JWK from public key
    jwk_dict = json.loads(ECAlgorithm.to_jwk(_test_public_key))

    # Patch the settings
    monkeypatch.setitem(settings.JWT_AUTH, "ES256_PUBLIC_JWK", jwk_dict)


def make_test_jwt(email: str, user_id: str, exp_minutes: int = 60) -> str:
    """Generate a test JWT token signed with test ES256 key."""
    payload = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(minutes=exp_minutes),
    }
    return jwt.encode(payload, TEST_ES256_PRIVATE_KEY, algorithm="ES256")
