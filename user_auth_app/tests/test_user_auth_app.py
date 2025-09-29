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
def test_create_user_sets_email_and_password():
    user = User.objects.create_user(email="a@b.com", password="test123")
    assert user.email == "a@b.com"
    assert user.check_password("test123")


@pytest.mark.django_db
def test_register_user_duplicate_email(client):
    User.objects.create_user(email="dupe@example.com", password="pw123")
    url = reverse("register")
    data = {
        "email": "dupe@example.com",
        "password": "securepassword",
        "confirmed_password": "securepassword",
    }
    response = client.post(url, data, format="json")

    assert response.status_code == 400
    assert "email" in response.data


@pytest.mark.django_db
def test_register_user_password_mismatch(client):
    url = reverse("register")
    data = {
        "email": "mismatch@example.com",
        "password": "password123",
        "confirmed_password": "different123",
    }
    response = client.post(url, data, format="json")

    assert response.status_code == 400
    assert "Passwords do not match" in str(response.data)


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


@pytest.mark.django_db
def test_password_reset_non_existing_email(client):
    response = client.post('/api/password_reset/', {"email": "no@user.com"})
    assert response.status_code == 200  


@pytest.mark.django_db
def test_password_reset_passwords_do_not_match(client):
    user = User.objects.create_user(email="resetmismatch@example.com", password="pw123")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    confirm_url = reverse("password_confirm", args=[uidb64, token])
    data = {"new_password": "newpw", "confirm_password": "differentpw"}
    response = client.post(confirm_url, data)

    assert response.status_code == 200
    assert "Passwords do not match" in str(response.data)


@pytest.mark.django_db
def test_password_reset_invalid_token(client):
    user = User.objects.create_user(email="invalidtoken@example.com", password="pw123")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    confirm_url = reverse("password_confirm", args=[uidb64, "invalidtoken"])
    response = client.post(confirm_url, {"new_password": "x", "confirm_password": "x"})

    assert response.status_code == 400
    assert "Ungültiger" in str(response.data)


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
def test_login_user_wrong_password(client):
    user = User.objects.create_user(email="wrongpw@example.com", password="correctpw")
    url = reverse("login")
    response = client.post(url, {"email": user.email, "password": "wrongpw"})
    assert response.status_code == 400
    assert "Invalid credentials" in str(response.data) or "ungültig" in str(response.data)


@pytest.mark.django_db
def test_login_user_non_existing(client):
    url = reverse("login")
    response = client.post(url, {"email": "notfound@example.com", "password": "pw"})
    assert response.status_code == 400
    assert "Invalid credentials" in str(response.data) or "ungültig" in str(response.data)


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
def test_token_refresh_without_cookie(client):
    url = reverse("token_refresh")
    response = client.post(url)
    assert response.status_code == 400
    assert "No refresh token" in str(response.data) or "Token" in str(response.data)


@pytest.mark.django_db
def test_token_refresh_invalid_cookie(client):
    client.cookies["refresh_token"] = "invalid"
    url = reverse("token_refresh")
    response = client.post(url)
    assert response.status_code == 401
    assert "Invalid refresh token" in str(response.data)    


@pytest.mark.django_db
def test_cookie_jwt_auth_invalid_cookie(client):
    client.cookies['access_token'] = 'invalid'
    response = client.get('/api/video/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_activate_view_invalid_token(client):
    response = client.get('/api/activate/invalid/invalid/')
    assert response.status_code == 400


@pytest.mark.django_db
def test_activate_view_invalid_uid(client):
    # invalid uid but valid token format
    user = User.objects.create_user(email="activefail@example.com", password="pw")
    token = default_token_generator.make_token(user)
    response = client.get(reverse("activate", args=["invaliduid", token]))
    assert response.status_code == 400