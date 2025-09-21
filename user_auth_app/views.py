from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token

from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer
from .utils import send_activation_email, send_password_reset_email, create_tokens_for_user, get_jwt_max_ages, set_auth_cookies


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

        
class ActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            return Response(
                    {"message": "Activation failed."},
                    status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response(
                    {"message": "Activation failed."},
                    status=status.HTTP_400_BAD_REQUEST
                )


def _cookie_settings():
    return dict(
        httponly=True,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", True), 
        samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
    )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh_token, access_token = create_tokens_for_user(user)
        access_max_age, refresh_max_age = get_jwt_max_ages()
        
        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username, 
                },  
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, request, access_token, refresh_token, access_max_age, refresh_max_age)

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return Response(
                    {"detail": "Refresh token missing."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist() 

            response = Response(
                {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
                status=status.HTTP_200_OK
            )

            response.delete_cookie("access_token", path="/")
            response.delete_cookie("refresh_token", path="/")
            response.delete_cookie("csrftoken", path="/")

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_max_age = int(
            getattr(settings, 'SIMPLE_JWT', {}) 
            .get('ACCESS_TOKEN_LIFETIME')
            .total_seconds()
        )
        
        resp = Response(
            {"detail": "Token refreshed", "access": str(new_access)},
            status=status.HTTP_200_OK,
        )
        
        resp.set_cookie(
            key="access_token",
            value=str(new_access),
            max_age=access_max_age,
            **_cookie_settings(),
        )

        return resp


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "E-Mail-Adresse erforderlich."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "An email has been sent to reset your password."},
                            status=status.HTTP_200_OK)

        send_password_reset_email(user)
        return Response({"message": "An email has been sent to reset your password."},
                        status=status.HTTP_200_OK)


class PasswordResetRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return redirect("http://localhost:5501/pages/auth/reset_password.html?token=invalid")

        if default_token_generator.check_token(user, token):
            return redirect(f"http://localhost:5501/pages/auth/reset_password.html?uid={uidb64}&token={token}")

        return redirect("http://localhost:5501/pages/auth/reset_password.html?token=invalid")



class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Neues Passwort erforderlich."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Ungültiger Link."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Token prüfen
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Ungültiger oder abgelaufener Token."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Passwort wurde erfolgreich geändert."},
                        status=status.HTTP_200_OK)



