import datetime

from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Favorite, Scholarship, ScholarshipRequest, User


class ModelTests(TestCase):
    def test_user_str(self):
        user = User.objects.create(name="Test User", email="test@example.com")
        self.assertEqual(str(user), "Test User")

    def test_scholarship_str(self):
        s = Scholarship.objects.create(
            section="IV",
            foundation_name="Test Foundation",
            scholarship_name="Test Scholarship",
        )
        self.assertEqual(str(s), "Test Scholarship - Test Foundation")

    def test_scholarship_request_str(self):
        user = User.objects.create(name="Test User", email="test@example.com")
        req = ScholarshipRequest.objects.create(
            user=user,
            scholarship_name="Brand New Scholarship",
            provider="Some Foundation",
        )
        self.assertIn("Brand New Scholarship", str(req))
        self.assertIn("pending", str(req))


class SubmissionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret-pass-123",
            name="Submittor",
        )

    def test_request_form_requires_login(self):
        response = self.client.get(reverse("request-form"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_request_form_authenticated_get(self):
        self.client.login(username="user@example.com", password="secret-pass-123")
        response = self.client.get(reverse("request-form"))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_pending_request(self):
        self.client.login(username="user@example.com", password="secret-pass-123")
        response = self.client.post(
            reverse("request-form"),
            data={
                "scholarship_name": "Future Scholarship",
                "provider": "Future Foundation",
                "award_amount": "30,000 JPY/month",
                "notes": "Please add this",
            },
        )
        self.assertEqual(response.status_code, 200)
        req = ScholarshipRequest.objects.get(user=self.user)
        self.assertEqual(req.status, "pending")
        self.assertEqual(req.scholarship_name, "Future Scholarship")
        self.assertEqual(req.provider, "Future Foundation")


class AdminReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="admin-pass-123",
            name="Admin",
        )
        self.submitter = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret-pass-123",
            name="Submittor",
        )
        self.req = ScholarshipRequest.objects.create(
            user=self.submitter,
            scholarship_name="To Be Approved",
            provider="Provider Co",
            award_amount="10,000 JPY/month",
        )

    def test_approve_creates_scholarship(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        before_count = Scholarship.objects.count()
        response = self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve", "admin_notes": "Looks good"},
        )
        self.assertEqual(response.status_code, 302)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "approved")
        self.assertEqual(Scholarship.objects.count(), before_count + 1)
        self.assertIsNotNone(self.req.created_scholarship)
        created = self.req.created_scholarship
        self.assertEqual(created.scholarship_name, "To Be Approved")
        self.assertEqual(created.foundation_name, "Provider Co")
        self.assertEqual(self.req.admin_notes, "Looks good")
        self.assertEqual(self.req.reviewed_by, self.admin)

    def test_approve_is_idempotent(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve"},
        )
        count_after_first = Scholarship.objects.count()
        self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve"},
        )
        self.assertEqual(Scholarship.objects.count(), count_after_first)

    def test_reject_does_not_create_scholarship(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        before_count = Scholarship.objects.count()
        response = self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "reject", "admin_notes": "Not eligible"},
        )
        self.assertEqual(response.status_code, 302)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "rejected")
        self.assertIsNone(self.req.created_scholarship)
        self.assertEqual(Scholarship.objects.count(), before_count)
        self.assertEqual(self.req.admin_notes, "Not eligible")

    def test_approve_links_existing_scholarship_on_duplicate(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        existing = Scholarship.objects.create(
            section="IV",
            foundation_name=self.req.provider,
            scholarship_name=self.req.scholarship_name,
        )
        before_count = Scholarship.objects.count()

        response = self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve", "admin_notes": "Already listed"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Scholarship.objects.count(), before_count)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "approved")
        self.assertEqual(self.req.created_scholarship, existing)
        self.assertEqual(self.req.reviewed_by, self.admin)

    def test_review_unknown_request_returns_404(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        missing_pk = 999999

        response_get = self.client.get(
            reverse("admin-request-detail", args=[missing_pk])
        )
        self.assertEqual(response_get.status_code, 404)

        response_post = self.client.post(
            reverse("admin-request-detail", args=[missing_pk]),
            data={"action": "approve"},
        )
        self.assertEqual(response_post.status_code, 404)

    def test_re_approve_keeps_same_created_scholarship(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve"},
        )
        self.req.refresh_from_db()
        first = self.req.created_scholarship
        self.assertIsNotNone(first)
        count = Scholarship.objects.count()

        self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve"},
        )

        self.assertEqual(Scholarship.objects.count(), count)
        self.req.refresh_from_db()
        self.assertEqual(self.req.created_scholarship_id, first.id)

    def test_detail_page_renders_for_pending_request(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        response = self.client.get(reverse("admin-request-detail", args=[self.req.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_renders_for_reviewed_request(self):
        self.client.login(username="admin@example.com", password="admin-pass-123")
        self.client.post(
            reverse("admin-request-detail", args=[self.req.pk]),
            data={"action": "approve", "admin_notes": "ok"},
        )
        response = self.client.get(reverse("admin-request-detail", args=[self.req.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin.name)


def make_scholarship(name, foundation=None, section="IV"):
    return Scholarship.objects.create(
        section=section,
        foundation_name=foundation or f"Foundation of {name}",
        scholarship_name=name,
    )


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u1@example.com",
            email="u1@example.com",
            password="pass-12345",
            name="User One",
        )
        self.scholarship = make_scholarship("Scholarship A")

    def test_favorite_fields_and_str(self):
        fav = Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.assertEqual(fav.user, self.user)
        self.assertEqual(fav.scholarship, self.scholarship)
        self.assertIsNotNone(fav.created_at)
        self.assertIn("User One", str(fav))
        self.assertIn("Scholarship A", str(fav))

    def test_unique_constraint_rejects_duplicate(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_cascade_delete_when_scholarship_removed(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.scholarship.delete()
        self.assertFalse(Favorite.objects.exists())

    def test_cascade_delete_when_user_removed(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.user.delete()
        self.assertFalse(Favorite.objects.exists())

    def test_ordering_most_recent_first(self):
        fav1 = Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        other = make_scholarship("Scholarship B")
        fav2 = Favorite.objects.create(user=self.user, scholarship=other)
        yesterday = timezone.now() - datetime.timedelta(days=1)
        Favorite.objects.filter(pk=fav1.pk).update(created_at=yesterday)
        ordered = list(Favorite.objects.all())
        self.assertEqual(ordered, [fav2, fav1])


class FavoriteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="fav@example.com",
            email="fav@example.com",
            password="pass-12345",
            name="Favoriter",
        )
        self.scholarship = make_scholarship("Faved Scholarship")

    def test_anonymous_toggle_redirects_to_login(self):
        response = self.client.post(
            reverse("toggle-favorite", args=[self.scholarship.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertFalse(Favorite.objects.exists())

    def test_anonymous_favorites_page_redirects_to_login(self):
        response = self.client.get(reverse("favorites"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_htmx_toggle_creates_then_removes(self):
        self.client.login(username="fav@example.com", password="pass-12345")
        url = reverse("toggle-favorite", args=[self.scholarship.pk])

        created = self.client.post(url, **{"HTTP_HX_REQUEST": "true"})
        self.assertEqual(created.status_code, 200)
        self.assertContains(created, "is-favorited")
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user, scholarship=self.scholarship
            ).exists()
        )

        removed = self.client.post(url, **{"HTTP_HX_REQUEST": "true"})
        self.assertEqual(removed.status_code, 200)
        self.assertNotContains(removed, "is-favorited")
        self.assertFalse(
            Favorite.objects.filter(
                user=self.user, scholarship=self.scholarship
            ).exists()
        )

    def test_toggle_never_creates_duplicate(self):
        self.client.login(username="fav@example.com", password="pass-12345")
        url = reverse("toggle-favorite", args=[self.scholarship.pk])
        self.client.post(url, **{"HTTP_HX_REQUEST": "true"})
        self.client.post(url, **{"HTTP_HX_REQUEST": "true"})
        self.client.post(url, **{"HTTP_HX_REQUEST": "true"})
        self.assertEqual(Favorite.objects.count(), 1)

    def test_non_htmx_toggle_redirects_to_detail(self):
        self.client.login(username="fav@example.com", password="pass-12345")
        response = self.client.post(
            reverse("toggle-favorite", args=[self.scholarship.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("scholarship-detail", args=[self.scholarship.pk]),
        )
        self.assertTrue(Favorite.objects.exists())

    def test_favorites_page_empty_state(self):
        self.client.login(username="fav@example.com", password="pass-12345")
        response = self.client.get(reverse("favorites"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "haven't saved")

    def test_favorites_page_lists_saved_scholarships(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.client.login(username="fav@example.com", password="pass-12345")
        response = self.client.get(reverse("favorites"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.scholarship.scholarship_name)
        self.assertContains(response, "is-favorited")


class FavoriteRenderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="r@example.com",
            email="r@example.com",
            password="pass-12345",
            name="Renderer",
        )
        self.scholarship = make_scholarship("Render Scholarship")

    def test_detail_shows_favorited_state_when_authed(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.client.login(username="r@example.com", password="pass-12345")
        response = self.client.get(
            reverse("scholarship-detail", args=[self.scholarship.pk])
        )
        self.assertContains(response, "is-favorited")

    def test_detail_shows_login_link_when_anonymous(self):
        response = self.client.get(
            reverse("scholarship-detail", args=[self.scholarship.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fav-login")

    def test_list_reflects_favorited_state_when_authed(self):
        Favorite.objects.create(user=self.user, scholarship=self.scholarship)
        self.client.login(username="r@example.com", password="pass-12345")
        response = self.client.get(
            reverse("scholarship-list") + "?scholarship_name=Render"
        )
        self.assertContains(response, "is-favorited")


class ScholarshipSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        for i in range(14):
            make_scholarship(f"Alpha Scholarship {i}", foundation=f"Alpha Found {i}")
        make_scholarship("Beta Award", foundation="Beta Found")

    def test_full_page_has_chrome_and_results(self):
        response = self.client.get(reverse("scholarship-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "filter-panel")
        self.assertContains(response, 'id="results"')

    def test_htmx_returns_fragment_only(self):
        response = self.client.get(
            reverse("scholarship-list"), **{"HTTP_HX_REQUEST": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")
        self.assertNotContains(response, "filter-panel")
        self.assertContains(response, 'id="results"')
        self.assertContains(response, "<th>Save</th>")

    def test_htmx_applies_filters(self):
        response = self.client.get(
            reverse("scholarship-list") + "?scholarship_name=Beta",
            **{"HTTP_HX_REQUEST": "true"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beta Award")
        self.assertNotContains(response, "Alpha Scholarship 0")

    def test_pagination_splits_results(self):
        response = self.client.get(reverse("scholarship-list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "page 2 of 2")
        self.assertContains(response, "15 scholarships found")

    def test_pagination_preserves_active_filters(self):
        response = self.client.get(
            reverse("scholarship-list") + "?scholarship_name=Alpha&page=1"
        )
        self.assertEqual(response.status_code, 200)
        # "Next" pagination link should carry the active filter forward
        self.assertContains(response, "scholarship_name=Alpha")
