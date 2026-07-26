from django.test import Client, TestCase
from django.urls import reverse

from .models import Scholarship, ScholarshipRequest, User


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
