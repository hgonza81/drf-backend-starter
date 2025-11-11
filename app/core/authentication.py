import jwt
from django.conf import settings
from rest_framework import authentication, exceptions


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication backend for verifying Supabase-issued JWTs.

    It expects an Authorization header in the format:
        Authorization: Bearer <token>

    The token is verified using the secret key defined in
    settings.SUPABASE["SECRET_KEY"] and decoded with algorithm HS256.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        # Skip if the request does not contain a valid Authorization header
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE["SECRET_KEY"],
                algorithms=["HS256"],
                audience="authenticated",  # Default audience for Supabase JWTs
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidAudienceError:
            raise exceptions.AuthenticationFailed("Invalid token audience")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user_id = payload.get("sub")
        user_email = payload.get("email")

        if not user_id:
            raise exceptions.AuthenticationFailed(
                "Missing 'sub' claim in token payload"
            )

        user = self.get_or_create_user(user_id, user_email)
        return (user, None)

    def get_or_create_user(self, user_id, email):
        """
        Helper method to map or create a Django user instance
        corresponding to the Supabase-authenticated user.

        You can adapt this to your own user model logic.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user, _ = User.objects.get_or_create(
            username=f"supabase_{user_id}",
            defaults={"email": email or ""},
        )
        return user
