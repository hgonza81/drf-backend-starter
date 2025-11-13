import json
import logging
import uuid

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using a JWT token.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # DRF: no credentials → let other authenticators run

        token = auth_header[len(self.keyword) :].strip()
        logger.debug("Authenticating JWT...")

        # Decode the token and validate structure
        try:
            payload = decode_jwt_auth_jwt(token)
        except exceptions.AuthenticationFailed:
            raise
        except Exception as exc:
            logger.exception("Unexpected JWT decoding failure.")
            raise exceptions.AuthenticationFailed("Invalid or expired token.") from exc

        # Extract user ID
        user_id = payload.get("sub")
        user_email = payload.get("email")

        if not user_id:
            raise exceptions.AuthenticationFailed("Token missing 'sub' claim.")

        # Convert to UUID
        try:
            user_uuid = uuid.UUID(str(user_id))
        except Exception as e:
            logger.warning("Invalid UUID format in token: %s", user_id)
            raise exceptions.AuthenticationFailed("Invalid user ID in token.") from e

        # Look up the local user
        try:
            user = User.objects.get(auth_id=user_uuid)
        except User.DoesNotExist as udne:
            logger.warning(
                "User %s (%s) in JWT not found in local DB.",
                user_email,
                user_uuid,
            )
            raise exceptions.AuthenticationFailed("User is not registered.") from udne

        logger.debug("User authenticated: %s", user.email)
        return (user, None)


def decode_jwt_auth_jwt(token: str) -> dict:
    """
    Decode a JWT using the correct algorithm (ES256).
    Validates signature, expiration, and audience.
    """
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")

        if alg != "ES256":
            raise exceptions.AuthenticationFailed(f"Unsupported JWT algorithm: {alg}")

        return _decode_es256(token)

    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed("Token has expired.") from exc
    except jwt.InvalidAudienceError as exc:
        raise exceptions.AuthenticationFailed("Invalid token audience.") from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed("Invalid token.") from exc


def _decode_es256(token: str) -> dict:
    """
    Decode an ES256 JWT using the public JWK provided in settings.
    """
    logger.debug("Decoding ES256 token...")

    jwk = settings.JWT_AUTH.get("ES256_PUBLIC_JWK")
    if not jwk:
        raise exceptions.AuthenticationFailed("ES256 public key not configured.")

    from jwt.algorithms import ECAlgorithm

    try:
        public_key = ECAlgorithm.from_jwk(json.dumps(jwk))
    except Exception as exc:
        logger.exception("Invalid ES256 JWK.")
        raise exceptions.AuthenticationFailed("Invalid ES256 public key.") from exc

    return jwt.decode(
        token,
        public_key,
        algorithms=["ES256"],
        audience="authenticated",
    )
