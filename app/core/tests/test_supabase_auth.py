import jwt
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.auth import SupabaseJWTAuthentication


# Simple DRF view to test authentication manually
class ProtectedView(APIView):
    authentication_classes = [SupabaseJWTAuthentication]

    def get(self, request):
        return Response({"message": "Authenticated", "user": str(request.user)})


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
    assert "testuser@example.com" in response.data["user"]


def test_supabase_jwt_auth_invalid_token():
    """
    This test ensures that invalid tokens are rejected properly.
    """
    invalid_token = "invalid.jwt.token"

    factory = APIRequestFactory()
    request = factory.get(
        "/protected-endpoint/",
        HTTP_AUTHORIZATION=f"Bearer {invalid_token}",
    )

    view = ProtectedView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
