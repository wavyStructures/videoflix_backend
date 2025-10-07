from rest_framework import serializers
from django.conf import settings
from django.core.mail import send_mail

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['id', 'email']
        

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users. Creating a new inactive user account (email confirmation required).
    """

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate(self, data):
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["password"]) 
        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,  
        )


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users.
    """
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive. Please activate via email first.")

        attrs["user"] = user
        return attrs

   