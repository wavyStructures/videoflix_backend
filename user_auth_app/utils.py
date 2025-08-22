from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_activation_email(user, token=None, uidb64=None):
    """
    Sends an account activation email to the user.
    Expects the token and uidb64 for the activation URL.
    """
    if not token or not uidb64:
        raise ValueError("Token and uidb64 are required to send activation email")

    activation_link = f"http://localhost:8000/api/activate/{uidb64}/{token}/"
    subject = "Activate your Videoflix account"
    message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n{activation_link}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


def send_password_reset_email(user, token=None, uidb64=None):
    """
    Sends a password reset email to the user.
    Expects the token and uidb64 for the reset URL.
    """
    if not token or not uidb64:
        raise ValueError("Token and uidb64 are required to send password reset email")

    reset_link = f"http://localhost:8000/api/password-reset-confirm/{uidb64}/{token}/"
    subject = "Reset your Videoflix password"
    message = f"Hi {user.username},\n\nPlease click the link below to reset your password:\n{reset_link}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
