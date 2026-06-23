from datetime import timezone
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

class DailyEntry(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    oxygen_purity = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.DecimalField(max_digits=6, decimal_places=2)
    flow_rate = models.DecimalField(max_digits=6, decimal_places=2)
    pdp = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.operator.username}"
