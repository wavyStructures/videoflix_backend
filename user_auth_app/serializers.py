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
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
        # extra_kwargs = {
        #     'email': {
        #         'required': True
        #     }
        # }   


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        # fields = ['username', 'email', 'password', 'confirmed_password']
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
        validate_password(data["password"])  # run Django's built-in validators
        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,  # must activate via email
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

         # If your CustomUser has USERNAME_FIELD = "email", this works out of the box.
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive. Please activate via email first.")

        attrs["user"] = user
        return attrs

    # def validate_confirmed_password(self, value):
    #     password = self.initial_data.get('password')
    #     if password and value and password != value:
    #         raise serializers.ValidationError('Passwords do not match')
    #     return value

    # def validate_email(self, value):
    #     if User.objects.filter(email=value).exists():
    #         raise serializers.ValidationError('Email already exists')
    #     return value

    # def save(self):
    #     pw = self.validated_data['password']

    #     account = User(email=self.validated_data['email'], username=self.validated_data['username'])
    #     account.set_password(pw)
    #     account.save()
    #     return account
    