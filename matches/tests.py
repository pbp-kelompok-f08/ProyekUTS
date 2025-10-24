from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.http import JsonResponse
import uuid

from .models import SportCategory, Match, Participation
from .forms import MatchForm, ParticipationForm, MatchSearchForm

CustomUser = get_user_model()


# ======================== MODEL TESTS ========================
class SportCategoryModelTest(TestCase):
    def test_slug_is_generated_on_save(self):
        category = SportCategory.objects.create(name="Sepak Bola")
        self.assertEqual(category.slug, "sepak-bola")
        self.assertEqual(str(category), "Sepak Bola")


class MatchModelTest(TestCase):
    def setUp(self):
        self.category = SportCategory.objects.create(name="Basket")
        self.match = Match.objects.create(
            title="Friendly Match",
            category=self.category,
            location="Lapangan UI",
            event_date=timezone.now() + timedelta(days=1),
            description="Main bareng aja",
            max_members=10,
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.match), "Friendly Match")

    def test_available_slots_and_current_members(self):
        user = CustomUser.objects.create(username="naufal")
        Participation.objects.create(match=self.match, user=user)
        self.assertEqual(self.match.current_members, 1)
        self.assertEqual(self.match.available_slots, 9)


class ParticipationModelTest(TestCase):
    def setUp(self):
        self.category = SportCategory.objects.create(name="Futsal")
        self.match = Match.objects.create(
            title="Turnamen Kampus",
            category=self.category,
            location="GOR Fasilkom",
            event_date=timezone.now() + timedelta(days=2),
            max_members=5,
        )
        self.user = CustomUser.objects.create(username="elgasing")

    def test_str_returns_user_and_match(self):
        participation = Participation.objects.create(match=self.match, user=self.user)
        self.assertIn(self.user.username, str(participation))
        self.assertIn(str(self.match.pk), str(participation))


# ======================== FORM TESTS ========================
class MatchFormTest(TestCase):
    def setUp(self):
        self.category = SportCategory.objects.create(name="Bulu Tangkis")

    def test_valid_form(self):
        form = MatchForm(
            data={
                "title": "Lomba Seru",
                "category": self.category.pk,
                "location": "Lapangan Senayan",
                "event_date": timezone.now() + timedelta(days=3),
                "description": "Turnamen harian",
                "max_members": 4,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_max_members(self):
        form = MatchForm(
            data={
                "title": "Match Invalid",
                "category": self.category.pk,
                "location": "Lapangan A",
                "event_date": timezone.now() + timedelta(days=1),
                "description": "Test error",
                "max_members": 0,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Jumlah maksimal anggota harus lebih dari nol.", form.errors["max_members"])

    def test_disabled_category_field_when_table_not_ready(self):
        # Simulasi table belum ready
        from matches import forms
        old_func = forms._is_category_table_ready
        forms._is_category_table_ready = lambda: False
        form = MatchForm()
        self.assertTrue(form.fields["category"].disabled)
        forms._is_category_table_ready = old_func


class ParticipationFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="tester")

    def test_message_field_optional(self):
        form = ParticipationForm(data={"user": self.user.pk, "message": ""})
        self.assertTrue(form.is_valid())


class MatchSearchFormTest(TestCase):
    def setUp(self):
        self.category = SportCategory.objects.create(name="Sepeda")

    def test_search_form_fields(self):
        form = MatchSearchForm(
            data={"category": self.category.pk, "keyword": "fun", "available_only": True}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["available_only"], True)

    def test_disabled_category_when_table_not_ready(self):
        from matches import forms
        old_func = forms._is_category_table_ready
        forms._is_category_table_ready = lambda: False
        form = MatchSearchForm()
        self.assertTrue(form.fields["category"].disabled)
        forms._is_category_table_ready = old_func


# ======================== VIEW TESTS ========================
class MatchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="player1", password="12345")
        self.client.login(username="player1", password="12345")

        from matches import views
        views._is_schema_ready = lambda: True

        self.category = SportCategory.objects.create(name="Sepak Bola")
        self.match = Match.objects.create(
            title="Uji Coba",
            category=self.category,
            location="Lapangan UI",
            event_date=timezone.now() + timedelta(days=1),
            description="Match Test",
            max_members=2,
        )

    def test_dashboard_view_status(self):
        response = self.client.get(reverse("matches:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_get_match_view(self):
        response = self.client.get(reverse("matches:get_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_create_match_view(self):
        response = self.client.post(
            reverse("matches:create_match"),
            {
                "title": "Match Baru",
                "category": self.category.pk,
                "location": "Lapangan B",
                "event_date": (timezone.now() + timedelta(days=2)).isoformat(),
                "description": "Test buat match",
                "max_members": 5,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])

    def test_create_match_invalid_form(self):
        response = self.client.post(
            reverse("matches:create_match"),
            {
                "title": "",
                "category": "",
                "location": "",
                "event_date": "",
                "description": "",
                "max_members": -1,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_book_match_view(self):
        response = self.client.post(reverse("matches:book_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_book_match_full(self):
        # Penuhi slot
        for i in range(2):
            u = CustomUser.objects.create_user(username=f"user{i}")
            Participation.objects.create(match=self.match, user=u)
        response = self.client.post(reverse("matches:book_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertIn("sudah penuh", str(response.json()))

    def test_prevent_double_join(self):
        self.client.post(reverse("matches:book_match", args=[self.match.pk]))
        response = self.client.post(reverse("matches:book_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Kamu sudah bergabung", str(response.json()))

    def test_delete_match_view_admin_only(self):
        self.user.role = "admin"
        self.user.save()
        response = self.client.delete(reverse("matches:delete_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 204)

    def test_delete_match_unauthorized(self):
        response = self.client.delete(reverse("matches:delete_match", args=[self.match.pk]))
        self.assertEqual(response.status_code, 401)

    def test_get_all_matches(self):
        response = self.client.get(reverse("matches:get_match"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_dashboard_ajax_request(self):
        response = self.client.get(
            reverse("matches:dashboard"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("groups", response.json())
        
        
from django.db.utils import OperationalError, ProgrammingError

class MatchEdgeCaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="tester", password="12345")
        self.client.login(username="tester", password="12345")
        self.category = SportCategory.objects.create(name="Lari")

    def test_schema_not_ready_in_dashboard(self):
        from matches import views
        old_func = views._is_schema_ready
        views._is_schema_ready = lambda: False
        response = self.client.get(reverse("matches:dashboard"))
        self.assertEqual(response.status_code, 503)
        views._is_schema_ready = old_func

    def test_create_match_schema_not_ready(self):
        from matches import views
        old_func = views._is_schema_ready
        views._is_schema_ready = lambda: False
        response = self.client.post(reverse("matches:create_match"), {})
        self.assertEqual(response.status_code, 503)
        self.assertIn("Database belum dimigrasikan", str(response.json()))
        views._is_schema_ready = old_func

    def test_book_match_schema_not_ready(self):
        from matches import views
        old_func = views._is_schema_ready
        views._is_schema_ready = lambda: False
        response = self.client.post(reverse("matches:book_match", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 503)
        views._is_schema_ready = old_func

    def test_delete_all_matches_as_admin(self):
        self.user.role = "admin"
        self.user.save()
        Match.objects.create(
            title="Test Delete All",
            category=self.category,
            location="Lapangan",
            event_date=timezone.now() + timedelta(days=1),
            max_members=5,
        )
        response = self.client.delete(reverse("matches:delete_match"))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Match.objects.count(), 0)

    def test_book_match_invalid_form(self):
        match = Match.objects.create(
            title="Bad Form",
            category=self.category,
            location="Tempat",
            event_date=timezone.now() + timedelta(days=1),
            max_members=3,
        )
        response = self.client.post(reverse("matches:book_match", args=[match.pk]), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])


    def test_is_schema_ready_handles_exceptions(self):
        from matches import views
        original_func = views.connection.introspection.table_names

        def raise_error():
            raise OperationalError("Simulated DB failure")

        views.connection.introspection.table_names = raise_error
        result = views._is_schema_ready()
        self.assertFalse(result)

        def raise_prog_error():
            raise ProgrammingError("Simulated programming error")

        views.connection.introspection.table_names = raise_prog_error
        result = views._is_schema_ready()
        self.assertFalse(result)

        # Restore original
        views.connection.introspection.table_names = original_func
        
        


