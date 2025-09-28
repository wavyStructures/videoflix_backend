from django.urls import reverse
from django.contrib.auth import get_user_model
import pytest
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


@pytest.mark.django_db
def test_register_user(client):
    url = reverse("register")  
    data = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "confirmed_password": "securepassword",
    }
    response = client.post(url, data, format="json")

    assert response.status_code == 201
    assert "user" in response.data
    assert response.data["user"]["email"] == "testuser@example.com"
    assert "token" in response.data


@pytest.mark.django_db
def test_activate_user(client):
    user = User.objects.create_user(
        email="inactive@example.com", password="securepassword", is_active=False
    )

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = reverse("activate", args=[uidb64, token])

    response = client.get(url)

    assert response.status_code == 200
    assert response.data["message"] == "Account successfully activated."
    user.refresh_from_db()
    assert user.is_active


@pytest.mark.django_db
def test_login_user(client):
    user = User.objects.create_user(
        email="loginuser@example.com", password="securepassword", is_active=True
    )
    url = reverse("login")
    data = {"email": user.email, "password": "securepassword"}
    response = client.post(url, data, format="json")

    assert response.status_code, 200
    assert response.data["detail"] == "Login successful"
    assert "user" in response.data
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies



@pytest.mark.django_db
def test_logout_user(client):
    user = User.objects.create_user(
        email="logoutuser@example.com", password="securepassword", is_active=True
    )
    login_url = reverse("login")
    client.post(login_url, {"email": user.email, "password": "securepassword"})

    logout_url = reverse("logout")
    response = client.post(logout_url)

    assert response.status_code == 200
    assert response.data["detail"].startswith("Logout successful")
    assert "access" not in response.cookies or response.cookies["access"].value == ""
    
    assert "refresh" not in response.cookies or response.cookies["refresh"].value == ""
    

@pytest.mark.django_db
def test_token_refresh(client):
    user = User.objects.create_user(
        email="refreshuser@example.com", password="securepassword", is_active=True
    )
    login_url = reverse("login")
    client.post(login_url, {"email": user.email, "password": "securepassword"})

    refresh_url = reverse("token_refresh")
    response = client.post(refresh_url)

    assert response.status_code == 200
    assert response.data["detail"] == "Token refreshed"
    assert "access" in response.data
    assert "access_token" in response.cookies


@pytest.mark.django_db
def test_password_reset_flow(client):
    user = User.objects.create_user(
        email="resetuser@example.com", password="oldpassword", is_active=True
    )
    reset_url = reverse("password_reset")
    response = client.post(reset_url, {"email": user.email})

    assert response.status_code == 200
    assert response.data["message"].startswith("An email has been sent")


    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    confirm_url = reverse("password_confirm", args=[uidb64, token])
    new_password_data = {
        "new_password": "newsecurepassword",
        "confirm_password": "newsecurepassword"
    }
    response = client.post(confirm_url, new_password_data)
    
    assert response.status_code == 200
    assert response.data["message"], "Passwort wurde erfolgreich geändert."
    
    user.refresh_from_db()
    assert user.check_password("newsecurepassword")

