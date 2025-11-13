import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


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
        auth_id="550e8400-e29b-41d4-a716-446655440000",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="userpass",
        is_staff=False,
        auth_id="550e8400-e29b-41d4-a716-446655440001",
    )


@pytest.fixture
def not_in_db_user(db):
    return User(
        email="new.user@example.com",
        password="userpass",
        is_staff=False,
        auth_id="550e8400-e29b-41d4-a716-446655440001",
    )
