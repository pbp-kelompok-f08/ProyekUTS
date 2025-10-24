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

    def test_logout_ajax(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("accounts:logout_ajax"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["success"])

    def test_register_ajax_success(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "pass12345",
            "password2": "pass12345",
        }
        response = self.client.post(
            reverse("accounts:register_ajax"),
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result["success"])
        self.assertTrue(CustomUser.objects.filter(username="newuser").exists())

    def test_register_ajax_fail(self):
        data = {
            "username": "",
            "email": "invalid",
            "password1": "123",
            "password2": "456",
        }
        response = self.client.post(
            reverse("accounts:register_ajax"),
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertFalse(result["success"])
        self.assertIn("errors", result)

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
        self.assertEqual(response.status_code, 302)

    def test_update_profile_with_picture(self):
        self.client.login(username="testuser", password="password123")
        image = SimpleUploadedFile("test.jpg", b"fake image content", content_type="image/jpeg")
        response = self.client.post(
            reverse("accounts:update_profile"),
            {"bio": "new bio", "profile_picture": image},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("profile_picture", data["data"])

    def test_update_profile_duplicate_email(self):
        CustomUser.objects.create_user(
            username="dupe",
            password="abc12345",
            email="dupe@mail.com",
            role="user"
        )
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("accounts:update_profile"),
            {"email": "dupe@mail.com"},
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("Email already taken", data["message"])

    def test_public_profile_existing_user(self):
        response = self.client.get(reverse("accounts:public_profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/public_profile.html")

    def test_public_profile_anonymous(self):
        response = self.client.get(reverse("accounts:public_profile", args=["anonymous"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/anonymous_profile.html")

    def test_public_profile_not_found(self):
        response = self.client.get(reverse("accounts:public_profile", args=["nonexistentuser"]))
        self.assertEqual(response.status_code, 404)

    def test_ajax_all_users_admin_success(self):
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(reverse("accounts:ajax_all_users"))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("users", data)
        self.assertIn("admins", data)
        self.assertIsInstance(data["users"], list)
        self.assertIsInstance(data["admins"], list)

