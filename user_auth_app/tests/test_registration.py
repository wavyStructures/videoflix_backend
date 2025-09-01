# user_auth_app/tests/test_auth.py
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_user(api_client):
    url = reverse("register")  # or your path: "/api/register/"
    data = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "confirmed_password": "securepassword",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert "user" in response.data
    assert response.data["user"]["email"] == "testuser@example.com"
    assert "token" in response.data


@pytest.mark.django_db
def test_activate_user(api_client):
    # Create inactive user manually
    user = User.objects.create_user(
        email="inactive@example.com", password="securepassword", is_active=False
    )
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from user_auth_app.tokens import account_activation_token  # adjust if needed

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    url = reverse("activate", args=[uidb64, token])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["message"] == "Account successfully activated."
    user.refresh_from_db()
    assert user.is_active


@pytest.mark.django_db
def test_login_user(api_client):
    user = User.objects.create_user(
        email="loginuser@example.com", password="securepassword", is_active=True
    )
    url = reverse("login")
    data = {"email": "loginuser@example.com", "password": "securepassword"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 200
    assert response.data["detail"] == "Login successful"
    assert "user" in response.data
    # Cookies should be set
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.django_db
def test_logout_user(api_client):
    user = User.objects.create_user(
        email="logoutuser@example.com", password="securepassword", is_active=True
    )
    login_url = reverse("login")
    api_client.post(login_url, {"email": user.email, "password": "securepassword"})
    logout_url = reverse("logout")
    response = api_client.post(logout_url)
    assert response.status_code == 200
    assert response.data["detail"].startswith("Logout successful")
    # Tokens should be removed
    assert "access_token" not in response.cookies or response.cookies["access_token"].value == ""
    assert "refresh_token" not in response.cookies or response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
def test_token_refresh(api_client):
    user = User.objects.create_user(
        email="refreshuser@example.com", password="securepassword", is_active=True
    )
    login_url = reverse("login")
    api_client.post(login_url, {"email": user.email, "password": "securepassword"})
    refresh_url = reverse("token_refresh")
    response = api_client.post(refresh_url)
    assert response.status_code == 200
    assert response.data["detail"] == "Token refreshed"
    assert "access" in response.data
    assert "access_token" in response.cookies


@pytest.mark.django_db
def test_password_reset_flow(api_client):
    user = User.objects.create_user(
        email="resetuser@example.com", password="oldpassword", is_active=True
    )

    # Request password reset
    reset_url = reverse("password_reset")
    response = api_client.post(reset_url, {"email": user.email})
    assert response.status_code == 200
    assert response.data["detail"].startswith("An email has been sent")

    # Simulate email link
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from user_auth_app.tokens import password_reset_token  # adjust if needed

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)
    confirm_url = reverse("password_confirm", args=[uidb64, token])
    new_password_data = {"new_password": "newsecurepassword", "confirm_password": "newsecurepassword"}
    response = api_client.post(confirm_url, new_password_data)
    assert response.status_code == 200
    assert response.data["detail"].startswith("Your Password has been successfully reset")
    user.refresh_from_db()
    assert user.check_password("newsecurepassword")
