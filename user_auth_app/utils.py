from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_activation_email(user):
    """
    Sends an account activation email to the given user.
    Generates uidb64 + token automatically and sends both
    plain text + HTML email versions.
    """

    # generate token + uid
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # build activation link (pointing to frontend)
    # activation_link = f"{settings.FRONTEND_URL}/activate/{uidb64}/{token}/"
    activation_link = f"{settings.FRONTEND_URL}/activate.html?uid={uidb64}&token={token}"


    # subject + message
    subject = "Videoflix - Bitte bestätigen Sie Ihre E-Mail-Adresse"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    text_content = f"Bitte aktivieren Sie Ihre E-Mail-Adresse: {activation_link}"
    html_content = f"""
        <p>Klicken Sie auf den Link, um Ihr Konto zu aktivieren:</p>
        <p><a href="{activation_link}">Konto aktivieren</a></p>
    """

    # send email
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_email(user):
    """
    Sendet eine E-Mail zum Zurücksetzen des Passworts.
    Generiert automatisch uidb64 + Token und verschickt sowohl
    Plain-Text- als auch HTML-Version.
    """

    # Token + uid erzeugen
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Reset-Link (zeigt auf das Frontend)
    reset_link = f"{settings.FRONTEND_URL}/password-reset-confirm/{uidb64}/{token}/"

    # Betreff + Nachricht
    subject = "Videoflix - Passwort zurücksetzen"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    text_content = (
        f"Hallo,\n\n"
        f"Sie haben eine Zurücksetzung Ihres Passworts angefordert.\n"
        f"Bitte klicken Sie auf den folgenden Link, um ein neues Passwort zu vergeben:\n\n"
        f"{reset_link}\n\n"
        f"Wenn Sie diese Anfrage nicht gestellt haben, können Sie diese E-Mail ignorieren."
    )

    html_content = f"""
        <p>Hallo,</p>
        <p>Sie haben eine Zurücksetzung Ihres Passworts angefordert.</p>
        <p>Klicken Sie auf den folgenden Link, um ein neues Passwort zu vergeben:</p>
        <p><a href="{reset_link}">Passwort zurücksetzen</a></p>
        <p>Wenn Sie diese Anfrage nicht gestellt haben, können Sie diese E-Mail ignorieren.</p>
    """

    # Mail versenden
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
