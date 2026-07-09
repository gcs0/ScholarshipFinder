from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    education = models.CharField(max_length=100, blank=True, default="")
    discipline = models.CharField(max_length=100, blank=True, default="")
    prefecture = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.name


class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    award_amount = models.IntegerField()
    education_level = models.CharField(max_length=100)
    discipline = models.CharField(max_length=100)
    prefecture = models.CharField(max_length=100)
    deadline = models.CharField(max_length=50)
    requirements = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class ScholarshipRequest(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scholarship_requests"
    )
    scholarship_name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    award_amount = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Request for {self.scholarship_name} by {self.user.name}"
