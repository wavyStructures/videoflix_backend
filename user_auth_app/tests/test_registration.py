from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UserAuthRegistrationTests(APITestCase):

    def test_register_user(self):
        url = reverse("register")  
        data = {
            "email": "testuser@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn ("user", response.data)
        self.assertEqual(response.data["user"]["email"], "testuser@example.com")
        self.assertIn ("token", response.data)


    def test_activate_user(self):
        user = User.objects.create_user(
            email="inactive@example.com", password="securepassword", is_active=False
        )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse("activate", args=[uidb64, token])
        response = self.client.get(url)
        self.assertEqual (response.status_code, 200)
        self.assertEqual (response.data["message"], "Account successfully activated.")
        user.refresh_from_db()
        self.assertTrue(user.is_active)


    def test_login_user(self):
        user = User.objects.create_user(
            email="loginuser@example.com", password="securepassword", is_active=True
        )
        url = reverse("login")
        data = {"email": "loginuser@example.com", "password": "securepassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Login successful")
        self.assertIn ("user", response.data)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)


    def test_logout_user(self):
        user = User.objects.create_user(
            email="logoutuser@example.com", password="securepassword", is_active=True
        )
        login_url = reverse("login")
        self.client.post(login_url, {"email": user.email, "password": "securepassword"})
        logout_url = reverse("logout")
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["detail"].startswith("Logout successful"))
        self.assertTrue(
            "access" not in response.cookies or response.cookies["access"].value == ""
        )
        self.assertTrue(
            "refresh" not in response.cookies or response.cookies["refresh"].value == ""
        )


    def test_token_refresh(self):
        user = User.objects.create_user(
            email="refreshuser@example.com", password="securepassword", is_active=True
        )
        login_url = reverse("login")
        self.client.post(login_url, {"email": user.email, "password": "securepassword"})
        refresh_url = reverse("token_refresh")
        response = self.client.post(refresh_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Token refreshed")
        self.assertIn("access", response.data)
        self.assertIn("access_token", response.cookies)



    def test_password_reset_flow(self):
        user = User.objects.create_user(
            email="resetuser@example.com", password="oldpassword", is_active=True
        )
        reset_url = reverse("password_reset")
        response = self.client.post(reset_url, {"email": user.email})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["message"].startswith("An email has been sent"))


        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        confirm_url = reverse("password_confirm", args=[uidb64, token])
        new_password_data = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }
        response = self.client.post(confirm_url, new_password_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Passwort wurde erfolgreich geändert.")

        
        user.refresh_from_db()
        self.assertTrue(user.check_password("newsecurepassword"))

