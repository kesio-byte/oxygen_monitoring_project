from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class DailyEntry(models.Model):
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='oxygen_entries'   # ✅ unique reverse accessor
    )
    date = models.DateField(auto_now_add=True, editable=False)
    time = models.TimeField(auto_now_add=True, editable=False)

    oxygen_purity = models.DecimalField(max_digits=5, decimal_places=2)  # %
    pressure = models.DecimalField(max_digits=6, decimal_places=2)       # bar/kPa
    flow_rate = models.DecimalField(max_digits=6, decimal_places=2)      # L/min
    pdp = models.DecimalField(max_digits=5, decimal_places=2)            # °C

    notes = models.TextField(blank=True, null=True)

    # Auto flags
    alert_status = models.BooleanField(default=False)
    critical_flag = models.BooleanField(default=False)

    # ✅ Field-level validation methods
    def clean_oxygen_purity(self):
        if self.oxygen_purity < 90 or self.oxygen_purity > 100:
            raise ValidationError("Oxygen purity must be between 90–100%.")

    def clean_pdp(self):
        if self.pdp > 0:
            raise ValidationError("PDP must be a negative value (below 0°C).")

    def clean(self):
        """Extra global validation if needed."""
        if self.pressure is not None and self.pressure <= 0:
            raise ValidationError({"pressure": "Pressure must be greater than zero."})


    def save(self, *args, **kwargs):
        # Auto‑flag logic
        if self.oxygen_purity < 93 or self.pdp > -55:
            self.alert_status = True
        if self.oxygen_purity < 93 and self.pdp > -55:
            self.critical_flag = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.operator.username}"
