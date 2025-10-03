from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CookieJWTAuthentication(BaseAuthentication):
    """
    Custom authentication class that authenticates users. Using a JWT stored in an HTTP cookie.
    """
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")
        if not token:
            return None
        try:
            access = AccessToken(token)
            user = User.objects.get(id=access["user_id"])
            return (user, None)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")


