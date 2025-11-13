import logging

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from supabase import Client, create_client

from app.jwt_auth.authentication import JWTAuthentication

logger = logging.getLogger(__name__)
User = get_user_model()


# Simple DRF view to test authentication manually
class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated", "user": str(request.user)})


@pytest.mark.django_db
def test_supabase_real_authentication():
    """
    This test authenticates with real Supabase credentials,
    gets a real JWT token, and verifies our authentication backend works.

    Uses credentials from environment variables for security.
    """
    import os

    # Get credentials from environment or skip test
    test_email = os.getenv("SUPABASE_AUTH_TEST_EMAIL", "")
    test_password = os.getenv("SUPABASE_AUTH_TEST_PASSWORD", "")

    # Create Supabase Auth API client
    supabase: Client = create_client(
        settings.JWT_AUTH["PROJECT_URL"], settings.JWT_AUTH["PUBLIC_KEY"]
    )

    # Authenticate with real credentials
    auth_response = supabase.auth.sign_in_with_password(
        {"email": test_email, "password": test_password}
    )

    # Get the access token and user ID from Supabase
    access_token = auth_response.session.access_token
    supabase_user_id = auth_response.user.id

    # Create the user in the local database (since our auth doesn't auto-create)
    User.objects.get_or_create(email=test_email, defaults={"auth_id": supabase_user_id})

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
    # The user email should be in the response
    assert test_email in response.data["user"]
    assert User.objects.filter(email=test_email, auth_id=supabase_user_id).exists(), (
        "User should exist locally with correct auth_id"
    )
