from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DailyEntry


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-input w-full", "placeholder": "Email address"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email


class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ["oxygen_purity", "pressure", "flow_rate", "pdp", "notes"]
        widgets = {
            "oxygen_purity": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                    "placeholder": "Enter oxygen purity (%) between 0–100%",
                    "class": "form-input w-full",
                }
            ),
            "pressure": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Enter pressure (bar) greater than 0",
                    "class": "form-input w-full",
                }
            ),
            "flow_rate": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Enter flow rate in L/min",
                    "class": "form-input w-full",
                }
            ),
            "pdp": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "max": "0",
                    "placeholder": "Enter PDP value (below 0°C)",
                    "class": "form-input w-full",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Optional notes",
                    "class": "form-textarea w-full",
                }
            ),
        }

    def clean_oxygen_purity(self):
        value = self.cleaned_data.get("oxygen_purity")
        if value is not None and not (0 <= value <= 100):
            raise forms.ValidationError("Oxygen purity must be between 0–100%.")
        return value

    def clean_pressure(self):
        value = self.cleaned_data.get("pressure")
        if value is not None and value <= 0:
            raise forms.ValidationError("Pressure must be greater than zero.")
        return value

    def clean_flow_rate(self):
        value = self.cleaned_data.get("flow_rate")
        if value is not None and value < 0:
            raise forms.ValidationError("Flow rate cannot be negative.")
        return value

    def clean_pdp(self):
        value = self.cleaned_data.get("pdp")
        if value is not None and value > 0:
            raise forms.ValidationError("PDP must be below 0°C.")
        return value