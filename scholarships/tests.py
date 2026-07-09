from django.test import TestCase

from .models import Scholarship, ScholarshipRequest, User


class ModelTests(TestCase):
    def test_user_str(self):
        user = User.objects.create(name="Test User", email="test@example.com")
        self.assertEqual(str(user), "Test User")

    def test_scholarship_str(self):
        s = Scholarship.objects.create(
            name="Test Scholarship",
            provider="Test Provider",
            award_amount=10000,
            education_level="Undergraduate",
            discipline="Computer Science",
            prefecture="Tokyo",
            deadline="2026-12-31",
        )
        self.assertEqual(str(s), "Test Scholarship")

    def test_scholarship_request_str(self):
        user = User.objects.create(name="Test User", email="test@example.com")
        req = ScholarshipRequest.objects.create(
            user=user,
            scholarship_name="New Scholarship",
            provider="New Provider",
        )
        self.assertIn("New Scholarship", str(req))
