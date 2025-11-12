from datetime import UTC, datetime, timedelta

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def make_supabase_jwt(email: str, sub: str | None = None, exp_minutes: int = 60):
    """Generate a fake Supabase-like JWT (signed locally with project secret)."""
    payload = {
        "sub": sub or "550e8400-e29b-41d4-a716-446655440000",
        "email": email,
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(minutes=exp_minutes),
    }
    return jwt.encode(payload, settings.SUPABASE["SECRET_KEY"], algorithm="HS256")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        email="admin@example.com", password="adminpass", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="user@example.com",
        password="userpass",
        is_staff=False,
        supabase_id="550e8400-e29b-41d4-a716-446655440000",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="userpass",
        is_staff=False,
        supabase_id="550e8400-e29b-41d4-a716-446655440001",
    )


@pytest.fixture
def supabase_token_user(regular_user):
    return make_supabase_jwt(regular_user.email, sub=regular_user.supabase_id)


@pytest.fixture
def supabase_token_other(another_user):
    return make_supabase_jwt(another_user.email, sub=another_user.supabase_id)
