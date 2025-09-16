from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Manager for 'CustomUser', authentification with email"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        
        if not extra_fields.get("username"):
            extra_fields["username"] = email
        
        extra_fields.setdefault("is_active", False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
        
class CustomUser(AbstractUser):
    """Videoflix user model. Username is kept for compatibility; email is unique."""

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)  
    address = models.CharField(max_length=255, null=True, blank=True)   
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []