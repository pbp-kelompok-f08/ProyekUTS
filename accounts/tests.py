import io
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import CustomUser


class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123", email="test@example.com", role="user"
        )
        self.admin = CustomUser.objects.create_user(
            username="adminuser", password="adminpass", email="admin@example.com", role="admin"
        )

    def test_register_ajax_valid(self):
        response = self.client.post(
            reverse("accounts:register_ajax"),
            json.dumps({
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "somepass123",
                "password2": "somepass123",
                "role": "user",
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["success"])

    def test_login_ajax_success(self):
        response = self.client.post(
            reverse("accounts:login_ajax"),
            json.dumps({"username": "testuser", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["success"])

    def test_login_ajax_fail(self):
        response = self.client.post(
            reverse("accounts:login_ajax"),
            json.dumps({"username": "testuser", "password": "wrong"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)["success"])

    def test_dashboard_user_access(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard_user.html")

    def test_dashboard_admin_access(self):
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard_admin.html")

    def test_profile_detail_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("accounts:profile_detail"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("username", data["data"])
        self.assertEqual(data["data"]["username"], "testuser")

    def test_profile_detail_unauthenticated(self):
        response = self.client.get(reverse("accounts:profile_detail"))
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_update_profile(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("accounts:update_profile"),
            {
                "username": "updateduser",
                "email": "newemail@example.com",
                "bio": "Updated bio",
                "favorite_sport": "F1",
                "skill_level": "expert"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["username"], "updateduser")

    def test_update_profile_with_picture(self):
        self.client.login(username="testuser", password="password123")
        image = SimpleUploadedFile("test.jpg", b"fake image content", content_type="image/jpeg")
        response = self.client.post(
            reverse("accounts:update_profile"),
            {"username": "picuser", "profile_picture": image},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("profile_picture", data["data"])

    def test_update_profile_no_username(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("accounts:update_profile"), {"username": ""})
        self.assertEqual(response.status_code, 400)

    def test_logout_ajax(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("accounts:logout_ajax"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["success"])
