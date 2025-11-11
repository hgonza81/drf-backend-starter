import jwt
from rest_framework import authentication, exceptions

SUPABASE_PROJECT_URL = "https://<your-project>.supabase.co"
SUPABASE_JWT_SECRET = "<your-jwt-secret>"  # En Supabase → Settings → API → JWT Secret


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        # Opcional: podés devolver un usuario dummy o mapearlo a tu modelo local
        user_id = payload.get("sub")
        user_email = payload.get("email")
        return ({"id": user_id, "email": user_email}, None)
