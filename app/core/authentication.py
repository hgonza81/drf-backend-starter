import json

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import jwt

User = get_user_model()


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication backend for verifying Supabase-issued JWTs.

    It expects an Authorization header in the format:
        Authorization: Bearer <token>

    Supports both HS256 (legacy) and ES256 (modern) algorithms.
    For ES256, it uses the public key from Supabase configuration.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        # Skip if the request does not contain a valid Authorization header
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            # First, check the token header to determine the algorithm
            unverified_header = jwt.get_unverified_header(token)
            algorithm = unverified_header.get("alg")

            if algorithm == "HS256":
                # Use the secret key for HS256 (legacy)
                payload = jwt.decode(
                    token,
                    settings.SUPABASE["SECRET_KEY"],
                    algorithms=["HS256"],
                    audience="authenticated",
                )
            elif algorithm == "ES256":
                # Use the public key for ES256 (modern)
                if not settings.SUPABASE.get("ES256_PUBLIC_JWK"):
                    raise exceptions.AuthenticationFailed(
                        "ES256 public key not configured"
                    )

                # Convert JWK to PEM format for PyJWT
                from jwt.algorithms import ECAlgorithm

                public_key = ECAlgorithm.from_jwk(
                    json.dumps(settings.SUPABASE["ES256_PUBLIC_JWK"])
                )

                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["ES256"],
                    audience="authenticated",
                )
            elif algorithm == "RS256":
                # Use JWKS for RS256 if needed
                from jwt import PyJWKClient

                jwks_url = (
                    f"{settings.SUPABASE['PROJECT_URL']}/auth/v1/.well-known/jwks.json"
                )
                jwks_client = PyJWKClient(jwks_url)
                signing_key = jwks_client.get_signing_key_from_jwt(token)

                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience="authenticated",
                )
            else:
                raise exceptions.AuthenticationFailed(
                    f"Unsupported algorithm: {algorithm}"
                )

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidAudienceError:
            raise exceptions.AuthenticationFailed("Invalid token audience")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except Exception:
            raise exceptions.AuthenticationFailed("Authentication failed")

        user_id = payload.get("sub")
        user_email = payload.get("email")

        if not user_id:
            raise exceptions.AuthenticationFailed(
                "Missing 'sub' claim in token payload"
            )

        user, _ = User.objects.get_or_create(
            supabase_id=user_id, defaults={"email": user_email or ""}
        )

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
