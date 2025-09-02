from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_activation_email(user):
    """
    Sends an account activation email to the given user.
    Generates uidb64 + token automatically and sends both
    plain text + HTML email versions.
    """

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_link = f"http://127.0.0.1:8000/api/activate/{uid}/{token}/"
    subject = "Videoflix - Activate your account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    text_content = f"Please click the link below to activate your account: {activation_link}"
    html_content = f"""
        <p>Please click the link below to activate your account:</p>
        <p><a href="{activation_link}">activating account</a></p>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_email(user):
    """
    Sends an email for password resetting.
    Generates uidb64 + token automatically and sends email.
    """

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = f"http://127.0.0.1:5501/pages/auth/confirm_password.html?uid={uid}&token={token}"

    subject = "Password Reset Request"
    message = f"Hi {user.email},\n\nClick the link below to reset your password:\n{reset_link}"
    user.email_user(subject, message)

