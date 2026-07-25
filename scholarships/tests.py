from django.test import TestCase

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
        scholarship = Scholarship.objects.create(
            section="IV",
            foundation_name="Test Foundation",
            scholarship_name="Test Scholarship",
        )
        req = ScholarshipRequest.objects.create(
            user=user,
            scholarship=scholarship,
        )
        self.assertIn("Test Scholarship", str(req))
        self.assertIn("pending", str(req))
