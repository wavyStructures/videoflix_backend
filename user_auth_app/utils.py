from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.timezone import now


def send_activation_email(user):
    """
    Sends an account activation email to the given user. Generates uidb64 + token automatically.
    """

    FRONTEND_URL = settings.FRONTEND_URL

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_link = f"{FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"
    subject = "Videoflix - Activate your account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    # text_content = f"Please click the link below to activate your account: {activation_link}"
    html_content = render_to_string("emails/account_activation.html", {
        "user": user,
        "activation_link": activation_link,
        "current_year": now().year
    })
    text_content = strip_tags(html_content)

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
    reset_link = f"{FRONTEND_URL}/pages/auth/confirm_password.html?uid={uid}&token={token}"

    subject = "Password Reset Request"

    context = {
        "user_email": user.email,
        "reset_link": reset_link
    }

    text_content = f"Hi {user.email},\n\nClick here to reset your password:\n{reset_link}"
    html_content = render_to_string("emails/password_reset.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def create_tokens_for_user(user):
    """Create and return (refresh_token_str, access_token_str) for a user."""
    
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return str(refresh), str(access)


def get_jwt_max_ages():
    """Return (access_max_age_seconds, refresh_max_age_seconds) or (None, None)
    if the corresponding SIMPLE_JWT settings are not present."""
    
    simple_jwt = getattr(settings, "SIMPLE_JWT", {})
    access_td = simple_jwt.get("ACCESS_TOKEN_LIFETIME")
    refresh_td = simple_jwt.get("REFRESH_TOKEN_LIFETIME")
    access_max_age = int(access_td.total_seconds()) if access_td is not None else None
    refresh_max_age = int(refresh_td.total_seconds()) if refresh_td is not None else None
    return access_max_age, refresh_max_age


def cookie_settings():
    """Common cookie flags used for auth cookies."""
    
    return {
    "httponly": True,
    "secure": getattr(settings, "SESSION_COOKIE_SECURE", True),
    "samesite": getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
    }


def set_auth_cookies(response, request, access_token, refresh_token, access_max_age=None, refresh_max_age=None):
    """
    Mutates the given DRF `Response` by setting access/refresh/csrf cookies and returns it.
    `access_max_age` / `refresh_max_age` may be None — in that case cookies are session cookies.
    """
    
    flags = cookie_settings()

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        **flags,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        **flags,
    )

    response.set_cookie(
        key="csrftoken",
        value=get_token(request),
        max_age=access_max_age,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", True),
        samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
        httponly=False,
    )

    return response