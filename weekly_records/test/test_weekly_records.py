from django.test import TestCase
from django.contrib.auth.models import User
from weekly_records.models import DailyEntry
from django.core.exceptions import ValidationError
from datetime import date

class TestDailyEntryValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

    def test_invalid_daily_entry_rejected(self):
        record = DailyEntry(
            operator=self.user,
            date=date.today(),
            oxygen_purity=150.0,  # invalid value
            pressure=5.0,
            flow_rate=10.0,
            pdp=-55.0,
        )
        with self.assertRaises(ValidationError):
            record.full_clean()
