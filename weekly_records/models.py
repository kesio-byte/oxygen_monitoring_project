from datetime import date, timezone
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


class DailyEntry(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    oxygen_purity = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.DecimalField(max_digits=6, decimal_places=2)
    flow_rate = models.DecimalField(max_digits=6, decimal_places=2)
    pdp = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.oxygen_purity < 0 or self.oxygen_purity > 100:
            raise ValidationError("Oxygen purity must be between 0 and 100.")

    def __str__(self):
        return f"{self.date} - {self.operator.username}"

def test_str_method(self):
    record = DailyEntry(
        operator=self.user,
        date=date.today(),
        oxygen_purity=95.0,
        pressure=5.0,
        flow_rate=10.0,
        pdp=-55.0,
    )
    self.assertIn("tester", str(record))
