from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    education = models.CharField(max_length=100, blank=True, default="")
    discipline = models.CharField(max_length=100, blank=True, default="")
    prefecture = models.CharField(max_length=100, blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name


class Scholarship(models.Model):
    SECTION_CHOICES = [
        ("III", "Local Govts & Intl Associations"),
        ("IV", "Private Foundations"),
        ("V", "For Applicants Residing Abroad"),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    foundation_name = models.CharField(max_length=500)
    scholarship_name = models.CharField(max_length=500)
    address_contact = models.TextField(blank=True, default="")
    inquiry = models.CharField(max_length=50, blank=True, default="")
    application = models.CharField(max_length=50, blank=True, default="")
    qualifier = models.CharField(max_length=200, blank=True, default="")
    designated_schools = models.TextField(blank=True, default="")
    designated_fields = models.TextField(blank=True, default="")
    PLURAL_GRANTS_CHOICES = [("Yes", "Yes"), ("No", "No"), ("Unknown", "Unknown")]
    plural_grants = models.CharField(
        max_length=7, choices=PLURAL_GRANTS_CHOICES, blank=True, default=""
    )
    additional_requirements = models.TextField(blank=True, default="")
    contents = models.TextField(blank=True, default="")
    duration = models.CharField(max_length=200, blank=True, default="")
    application_period = models.CharField(max_length=200, blank=True, default="")
    selection_method = models.CharField(max_length=200, blank=True, default="")
    grantees = models.CharField(max_length=100, blank=True, default="")
    grantees_applications = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["foundation_name", "scholarship_name"]
        ordering = ["section", "foundation_name", "scholarship_name"]

    def __str__(self):
        return f"{self.scholarship_name} - {self.foundation_name}"


class ScholarshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scholarship_requests"
    )
    scholarship_name = models.CharField(max_length=500)
    provider = models.CharField(max_length=500)
    award_amount = models.CharField(max_length=200, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_from_request",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_notes = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_requests",
    )
    reviewed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Request to add '{self.scholarship_name}' by {self.user.name} "
            f"({self.status})"
        )


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    scholarship = models.ForeignKey(
        Scholarship, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "scholarship"], name="uniq_user_scholarship_fav"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.name} ★ {self.scholarship.scholarship_name}"
