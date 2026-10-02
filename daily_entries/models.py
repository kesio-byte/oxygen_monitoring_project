from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Technician(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class DailyEntry(models.Model):
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oxygen_entries",
    )

    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    oxygen_purity = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.DecimalField(max_digits=6, decimal_places=2)
    flow_rate = models.DecimalField(max_digits=6, decimal_places=2)
    pdp = models.DecimalField(max_digits=5, decimal_places=2)

    notes = models.TextField(blank=True, null=True)

    alert_status = models.BooleanField(default=False)
    critical_flag = models.BooleanField(default=False)
    technician_ack = models.BooleanField(default=False)

    def __str__(self):
        operator_name = self.operator.username if self.operator_id else "No Operator"
        return f"{self.date} - {operator_name}"

    def clean(self):
        errors = {}

        if self.oxygen_purity is not None and not (0 <= self.oxygen_purity <= 100):
            errors["oxygen_purity"] = "Oxygen purity must be between 0 and 100%."

        if self.pdp is not None and self.pdp > 0:
            errors["pdp"] = "PDP must be a negative value (below 0°C)."

        if self.pressure is not None and self.pressure <= 0:
            errors["pressure"] = "Pressure must be greater than zero."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())

        if not self.date:
            self.date = now.date()
        if not self.time:
            self.time = now.time().replace(second=0, microsecond=0)

        self.full_clean()

        self.alert_status = (
            self.oxygen_purity < 93.0
            or self.pressure < 5.0  # replace with your actual threshold
            or self.flow_rate < 0   # replace with your actual threshold
            or self.pdp > -55.0
        )
        self.critical_flag = (
            self.oxygen_purity < 93.0
            and self.pdp > -55.0
        )

        super().save(*args, **kwargs)