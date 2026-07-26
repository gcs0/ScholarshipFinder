import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import Scholarship, ScholarshipRequest, User

# Import qualifier mapping for data cleaning
try:
    from .templatetags.scholarship_extras import QUALIFIER_MAPPING
except ImportError:
    QUALIFIER_MAPPING = {}

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
        fields = (
            "name",
            "email",
            "education",
            "discipline",
            "prefecture",
            "password1",
            "password2",
        )

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
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Enter your email address", "autocomplete": "email"}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})


class ScholarshipRequestForm(forms.ModelForm):
    class Meta:
        model = ScholarshipRequest
        fields = ["scholarship"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scholarship"].widget.attrs.update({"class": "form-select"})


class ScholarshipFilterForm(forms.Form):
    section = forms.ChoiceField(choices=[], required=False, label="Scholarship Type")
    scholarship_name = forms.CharField(required=False, label="Scholarship Name")
    qualifier = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label="School Year",
        widget=forms.CheckboxSelectMultiple,
    )
    designated_schools = forms.CharField(required=False, label="Designated Schools")
    designated_fields = forms.CharField(required=False, label="Fields of Study")
    plural_grants = forms.ChoiceField(
        choices=[], required=False, label="Multiple Grants"
    )
    award_amount_min = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=600000,
        label="Minimum Award (¥/month)",
        help_text="Enter minimum monthly award amount. Variable amounts will always be included.",
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 50000", "step": "1000"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        section_choices = [("", "All")] + list(Scholarship.SECTION_CHOICES)
        self.fields["section"].choices = section_choices

        self.fields["qualifier"].choices = self._get_qualifier_choices()

        self.fields["plural_grants"].choices = [
            ("", "All"),
            ("Yes", "Yes"),
            ("No", "No"),
            ("Unknown", "Unknown"),
        ]

    def _get_qualifier_choices(self):
        # Use a dictionary to track display names and their base codes
        display_name_to_base_code = {}

        for qualifier_str in Scholarship.objects.values_list(
            "qualifier", flat=True
        ).distinct():
            if qualifier_str:
                # Clean and normalize the qualifier string
                cleaned_str = qualifier_str.strip()
                # Replace full-width characters with ASCII equivalents
                cleaned_str = (
                    cleaned_str.replace("Ｍ", "M")
                    .replace("Ｄ", "D")
                    .replace("）", ")")
                    .replace("（", "(")
                )
                # Split by newlines and process each code
                codes = [
                    code.strip() for code in cleaned_str.split("\n") if code.strip()
                ]

                for code in codes:
                    # Extract base qualifier code (e.g., extract "U" from "U(2-3)" or "U2")
                    # Only include codes that start with letters followed by optional digits
                    if re.match(r"^[A-Za-z]+(?:\d+)?(?:\s*[\(,\-]|$)", code):
                        # Extract the base code for mapping lookup
                        base_code_match = re.match(r"^([A-Za-z]+)(?:\d+)?", code)
                        if base_code_match:
                            base_code = base_code_match.group(1)
                            # Only use codes that exist in QUALIFIER_MAPPING
                            if base_code in QUALIFIER_MAPPING:
                                display_name = QUALIFIER_MAPPING[base_code]
                                # Store the base code for this display name (first one wins)
                                if display_name not in display_name_to_base_code:
                                    display_name_to_base_code[display_name] = base_code

        # Create choices from display names and their base codes
        qualifier_choices = [
            (base_code, display_name)
            for display_name, base_code in sorted(display_name_to_base_code.items())
        ]

        return qualifier_choices
