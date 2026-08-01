from django.test import TestCase
from django.contrib.auth.models import User
from daily_entries.models import DailyEntry

class TestDailyEntryModel(TestCase):
    def test_entry_creation(self):
        user = User.objects.create(username="kesio")
        entry = DailyEntry.objects.create(
            operator=user,
            oxygen_purity=95.0,
            pressure=5.0,
            flow_rate=10.0,
            pdp=-60.0
        )
        self.assertEqual(entry.oxygen_purity, 95.0)
        self.assertEqual(entry.operator.username, "kesio")
