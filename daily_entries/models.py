# ----- My  Daily entries models.py file ------

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# ------- class Technician model -------
class Technician(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)

    # Define the string representation of the Tech model
    def __str__(self):
        return self.name


# ------- class DailyEntry model -------
class DailyEntry(models.Model):

    # Define the fields for the DailyEntry model
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

    # Define the str representation of the DailyEntry model
    def __str__(self):
        operator_name = self.operator.username if self.operator_id else "No Operator"
        return f"{self.date} - {operator_name}"

    # Validate values to help ensure data integrity
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

    # Override save to set missing date/time values, calculate flags,
    # validate the instance, and then save it to the database.
    def save(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())

        # Set date and time to the current local values if they are missing.
        if not self.date:
            self.date = now.date()

        if not self.time:
            self.time = now.time().replace(second=0, microsecond=0)

        # Set alert status based on the configured operating thresholds.
        self.alert_status = (
            self.oxygen_purity < 93.0
            or self.pressure < 5.0
            or self.flow_rate < 0
            or self.pdp > -55.0
        )

        # Mark the entry critical when both conditions are mt.
        self.critical_flag = (
            self.oxygen_purity < 93.0
            and self.pdp > -55.0
        )

        # Run model and field validation before saving.
        self.full_clean()

        # Save the instance to the database.
        super().save(*args, **kwargs)

# End of models.py