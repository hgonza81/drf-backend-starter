import logging

from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from app.core.jwt_auth.jwt_utils import decode_supabase_jwt

logger = logging.getLogger(__name__)
User = get_user_model()


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using Supabase-issued JWT tokens.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()
        logger.debug("Authenticating Supabase JWT...")

        payload = decode_supabase_jwt(token)
        user_id = payload.get("sub")
        user_email = payload.get("email")

        if not user_id:
            raise exceptions.AuthenticationFailed(
                "Missing 'sub' claim in token payload."
            )

        try:
            user, created = User.objects.get_or_create(
                supabase_id=user_id,
                defaults={"email": user_email or ""},
            )
            if created:
                logger.info("Created new user from Supabase token: %s", user_email)
            else:
                logger.debug("Authenticated existing user: %s", user_email)
        except Exception as exc:
            logger.exception("Error syncing Supabase user to local DB.")
            raise exceptions.AuthenticationFailed(
                "User synchronization failed."
            ) from exc

        return (user, None)
