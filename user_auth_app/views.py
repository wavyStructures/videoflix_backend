from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (RegistrationSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer)
from .utils import send_activation_email, send_password_reset_email

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        # generate activation token
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"http://localhost:8000/api/activate/{uidb64}/{token}/"

        # send activation email (simplified, you can adapt for Redis/SMTP later)
        send_mail(
            subject="Activate your Videoflix account",
            message=f"Click here to activate your account: {activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # return token (demo purpose only, frontend ignores)
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
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)
        
        

def _cookie_settings():
    # Centralize cookie security flags
    return dict(
        httponly=True,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", True),  # True in prod (HTTPS)
        samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
    )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Lifetimes (to set cookie max_age)
        access_max_age = int(getattr(settings, "SIMPLE_JWT", {}) \
                             .get("ACCESS_TOKEN_LIFETIME").total_seconds())
        refresh_max_age = int(getattr(settings, "SIMPLE_JWT", {}) \
                              .get("REFRESH_TOKEN_LIFETIME").total_seconds())

        resp = Response(
            {
                "detail": "Login successful",
                "user": UserSerializer(user).data,  # {"id": ..., "email": ...}
            },
            status=status.HTTP_200_OK,
        )

        # HttpOnly cookies (frontend does not read them — browser attaches them automatically)
        cookie_flags = _cookie_settings()
        resp.set_cookie(
            key="access_token",
            value=str(access),
            max_age=access_max_age,
            **cookie_flags,
        )
        resp.set_cookie(
            key="refresh_token",
            value=str(refresh),
            max_age=refresh_max_age,
            **cookie_flags,
        )

        return resp

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # requires Blacklist app enabled
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resp = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        # Clear cookies
        resp.delete_cookie("access_token")
        resp.delete_cookie("refresh_token")

        return resp


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
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

        access_max_age = int(getattr(settings, "SIMPLE_JWT", {}) \
                             .get("ACCESS_TOKEN_LIFETIME").total_seconds())

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



# class LogoutView(APIView):
#     def post(self, request):
#         return Response({"message": "User logged out"}, status=status.HTTP_200_OK)

# class RefreshTokenView(APIView):
#     def post(self, request):
#         return Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request):
        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)


class PasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        return Response({"message": f"Password confirmed for {uidb64}"}, status=status.HTTP_200_OK)


# class RegistrationView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegistrationSerializer(data=request.data)

#         data = {}
#         if serializer.is_valid():
#             saved_account = serializer.save()
#             data = {
#                 'username': saved_account.username,
#                 'email': saved_account.email,
#                 'user_id': saved_account.pk
#             }
#             return Response(data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RegisterView(APIView):
#     def post(self, request):
#         return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)
        

# class ActivateAccountView(APIView):
#     def get(self, request, uidb64, token):
#         return Response({"message": f"Account activated for {uidb64}"}, status=status.HTTP_200_OK)

# class LoginView(APIView):
#     def post(self, request):
#         return Response({"message": "User logged in"}, status=status.HTTP_200_OK)
