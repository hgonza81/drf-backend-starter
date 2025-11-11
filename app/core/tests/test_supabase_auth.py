import pytest
import jwt
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from supabase import create_client, Client

from app.core.authentication import SupabaseJWTAuthentication


# Simple DRF view to test authentication manually
class ProtectedView(APIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated", "user": str(request.user)})


@pytest.mark.django_db
def test_supabase_jwt_auth_success():
    """
    This test generates a valid Supabase-like JWT locally,
    then verifies that the custom authentication class can decode it correctly.
    """
    # Generate a test JWT token using the same secret as Supabase (from settings)
    payload = {
        "sub": "12345",
        "email": "testuser@example.com",
        "aud": "authenticated",  # Must match the 'audience' parameter
    }
    token = jwt.encode(payload, settings.SUPABASE["SECRET_KEY"], algorithm="HS256")

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Authenticated"
    assert "supabase_12345" in response.data["user"]


def test_supabase_jwt_auth_invalid_token():
    """
    This test ensures that invalid tokens are rejected properly.
    When authentication fails and returns None, DRF checks permissions.
    Since IsAuthenticated is required and user is not authenticated, it returns 403.
    """
    invalid_token = "invalid.jwt.token"

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {invalid_token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    # DRF returns 403 when authentication returns None and permission is required
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_supabase_real_authentication():
    """
    This test authenticates with real Supabase credentials,
    gets a real JWT token, and verifies our authentication backend works.

    Uses credentials from environment variables for security.
    """
    import os

    # Get credentials from environment or skip test
    test_email = os.getenv("SUPABASE_TEST_EMAIL", "hernan.gonzalez81@gmail.com")
    test_password = os.getenv("SUPABASE_TEST_PASSWORD", "wkh@frf.rhx*vwb7MUG")

    # Create Supabase client
    supabase: Client = create_client(
        settings.SUPABASE["PROJECT_URL"], settings.SUPABASE["PUBLIC_KEY"]
    )

    # Authenticate with real credentials
    auth_response = supabase.auth.sign_in_with_password(
        {"email": test_email, "password": test_password}
    )

    # Get the access token
    access_token = auth_response.session.access_token

    # Test our authentication backend with the real token
    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Authenticated"
    # The user should be created based on the Supabase user ID
    assert "supabase_" in response.data["user"]
