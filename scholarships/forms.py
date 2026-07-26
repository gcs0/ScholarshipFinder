from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import forms as auth_forms
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
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update({"placeholder": "Enter your email address", "autocomplete": "email"})
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
    qualifier = forms.MultipleChoiceField(choices=[], required=False, label="School Year", widget=forms.CheckboxSelectMultiple)
    designated_schools = forms.CharField(required=False, label="Designated Schools")
    designated_fields = forms.CharField(required=False, label="Fields of Study")
    plural_grants = forms.ChoiceField(choices=[], required=False, label="Multiple Grants")
    contents = forms.CharField(required=False, label="Award Amount")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        section_choices = [("", "All")] + list(Scholarship.SECTION_CHOICES)
        self.fields["section"].choices = section_choices
        
        self.fields["qualifier"].choices = self._get_qualifier_choices()
        
        plural_grants_values = (
            Scholarship.objects.values_list("plural_grants", flat=True)
            .distinct()
            .exclude(plural_grants="")
            .order_by("plural_grants")
        )
        plural_grants_choices = [("", "All")] + [(v, v) for v in plural_grants_values]
        self.fields["plural_grants"].choices = plural_grants_choices

    def _get_qualifier_choices(self):
        all_qualifiers = set()
        for qualifier_str in Scholarship.objects.values_list("qualifier", flat=True).distinct():
            if qualifier_str:
                codes = [code.strip() for code in qualifier_str.split('\n') if code.strip()]
                all_qualifiers.update(codes)
        
        try:
            from .templatetags.scholarship_extras import QUALIFIER_MAPPING
        except ImportError:
            QUALIFIER_MAPPING = {}
            
        qualifier_choices = []
        for code in sorted(all_qualifiers):
            display_name = QUALIFIER_MAPPING.get(code, code)
            qualifier_choices.append((code, f"{code} - {display_name}"))
        
        return qualifier_choices
