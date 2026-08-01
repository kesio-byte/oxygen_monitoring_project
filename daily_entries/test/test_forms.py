from django.test import TestCase
from django.contrib.auth.models import User
from daily_entries.forms import DailyEntryForm
from datetime import date, time

class TestDailyEntryForm(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="kesio")

    def test_valid_form(self):
        form_data = {
            "date": date.today(),
            "time": time(9, 0),
            "oxygen_purity": 95.0,
            "pressure": 5.0,
            "flow_rate": 10.0,
            "pdp": -60.0,
        }
        form = DailyEntryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_negative_purity(self):
        form_data = {
            "date": date.today(),
            "time": time(9, 0),
            "oxygen_purity": -5.0,   # ❌ invalid
            "pressure": 5.0,
            "flow_rate": 10.0,
            "pdp": -60.0,
        }
        form = DailyEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("oxygen_purity", form.errors)

    def test_missing_required_field(self):
        form_data = {
            "date": date.today(),
            "time": time(9, 0),
            # ❌ missing oxygen_purity
            "pressure": 5.0,
            "flow_rate": 10.0,
            "pdp": -60.0,
        }
        form = DailyEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("oxygen_purity", form.errors)
