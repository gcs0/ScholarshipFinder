from django import forms

from .models import Scholarship, ScholarshipRequest, User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "email", "education", "discipline", "prefecture"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ScholarshipRequestForm(forms.ModelForm):
    class Meta:
        model = ScholarshipRequest
        fields = ["user", "scholarship_name", "provider", "award_amount", "notes"]
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
