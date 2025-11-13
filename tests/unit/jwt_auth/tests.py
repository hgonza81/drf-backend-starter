import logging

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from app.jwt_auth.authentication import JWTAuthentication
from tests.unit.jwt_auth.conftest import make_test_jwt

logger = logging.getLogger(__name__)
User = get_user_model()


# Simple DRF view to test authentication manually
class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated", "user": str(request.user)})


@pytest.mark.django_db
def test_jwt_auth_success():
    """
    Test that a valid JWT token is decoded correctly and authenticates the user.
    """
    test_user_id = "550e8400-e29b-41d4-a716-446655440000"
    test_email = "testuser@example.com"

    # Generate a test JWT token
    token = make_test_jwt(email=test_email, user_id=test_user_id)

    # Create the user in the local database
    User.objects.get_or_create(email=test_email, defaults={"auth_id": test_user_id})

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Authenticated"
    assert test_email in response.data["user"]


def test_jwt_auth_invalid_token():
    """
    Test that invalid tokens are rejected properly.
    """
    invalid_token = "invalid.jwt.token"

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {invalid_token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    # DRF returns 403 when authentication fails and permission is required
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_jwt_auth_missing_user():
    """
    Test that authentication fails when the user doesn't exist in the database.
    """
    test_user_id = "550e8400-e29b-41d4-a716-446655440099"
    test_email = "nonexistent@example.com"

    # Generate a valid token but don't create the user
    token = make_test_jwt(email=test_email, user_id=test_user_id)

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    # Should fail because user doesn't exist in database
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_jwt_auth_no_token():
    """
    Test that requests without a token are not authenticated.
    """
    factory = APIRequestFactory()
    request = factory.get("/protected-endpoint/")

    view = ProtectedView.as_view()
    response = view(request)

    # Should fail because no authentication provided
    assert response.status_code == status.HTTP_403_FORBIDDEN
