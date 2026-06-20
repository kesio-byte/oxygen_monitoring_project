# daily_entries/forms.py
from django import forms
from .models import DailyEntry

class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['oxygen_purity', 'pressure', 'flow_rate', 'pdp', 'notes']
        help_texts = {
            'oxygen_purity': "Enter a value between 90–100%",
            'pressure': "Pressure must be greater than 0 bar",
            'flow_rate': "Flow rate in L/min",
            'pdp': "Enter dew point below 0°C (negative values)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oxygen_purity'].widget.attrs.update({
            'placeholder': 'Enter oxygen purity (%)',
            'class': 'form-input w-full'
        })
        self.fields['pressure'].widget.attrs.update({
            'placeholder': 'Enter pressure (bar)',
            'class': 'form-input w-full'
        })
        self.fields['flow_rate'].widget.attrs.update({
            'placeholder': 'Enter flow rate',
            'class': 'form-input w-full'
        })
        self.fields['pdp'].widget.attrs.update({
            'placeholder': 'Enter PDP value',
            'class': 'form-input w-full'
        })
        self.fields['notes'].widget.attrs.update({
            'placeholder': 'Optional notes',
            'class': 'form-textarea w-full'
        })

    # ✅ Field-level validation methods
    def clean_oxygen_purity(self):
        value = self.cleaned_data.get('oxygen_purity')
        if value < 90 or value > 100:
            raise forms.ValidationError("Oxygen purity must be between 90–100%.")
        return value

    def clean_pdp(self):
        value = self.cleaned_data.get('pdp')
        if value > 0:
            raise forms.ValidationError("PDP must be a negative value (below 0°C).")
        return value

    def clean_pressure(self):
        value = self.cleaned_data.get('pressure')
        if value <= 0:
            raise forms.ValidationError("Pressure must be greater than zero.")
        return value
