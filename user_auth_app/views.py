from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.pk
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class RegisterView(APIView):
    def post(self, request):
        return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)
        

class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        return Response({"message": f"Account activated for {uidb64}"}, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        return Response({"message": "User logged in"}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "User logged out"}, status=status.HTTP_200_OK)

class RefreshTokenView(APIView):
    def post(self, request):
        return Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request):
        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)


class PasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        return Response({"message": f"Password confirmed for {uidb64}"}, status=status.HTTP_200_OK)
