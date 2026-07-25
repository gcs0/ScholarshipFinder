from django import forms
from django.contrib.auth import authenticate, get_user_model, forms as auth_forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

from .models import Scholarship, ScholarshipRequest, User

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "email", "education", "discipline", "prefecture"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("name", "email", "education", "discipline", "prefecture", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "Enter your email"})
        self.fields["name"].widget.attrs.update({"placeholder": "Enter your full name"})
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Enter a password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm your password"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "Username or Email"})
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})


class ScholarshipRequestForm(forms.ModelForm):
    class Meta:
        model = ScholarshipRequest
        fields = ["scholarship_name", "provider", "award_amount", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}

    def clean_award_amount(self):
        amount = self.cleaned_data.get("award_amount")
        if amount is not None and amount < 0:
            raise forms.ValidationError("Award amount must be a positive number.")
        return amount


class ScholarshipFilterForm(forms.Form):
    education_level = forms.ChoiceField(choices=[], required=False)
    discipline = forms.ChoiceField(choices=[], required=False)
    prefecture = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["education_level"].choices = self._get_choices("education_level")
        self.fields["discipline"].choices = self._get_choices("discipline")
        self.fields["prefecture"].choices = self._get_choices("prefecture")

    def _get_choices(self, field_name):
        values = (
            Scholarship.objects.values_list(field_name, flat=True)
            .distinct()
            .order_by(field_name)
        )
        return [("", "All")] + [(v, v) for v in values if v]
