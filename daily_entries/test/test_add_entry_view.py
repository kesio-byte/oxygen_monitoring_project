from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from daily_entries.models import DailyEntry
from datetime import date

class TestAddEntryView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="kesio", password="password")
        self.client.login(username="kesio", password="password")

    @patch("daily_entries.views.send_alert_sms")
    def test_add_entry_triggers_sms_on_low_purity(self, mock_sms):
        form_data = {
            "date": date.today().isoformat(),
            "time": "09:00:00",
            "oxygen_purity": "85.0",
            "pressure": "5.0",
            "flow_rate": "10.0",
            "pdp": "-60.0",
        }
        response = self.client.post(reverse("daily_entry_form"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DailyEntry.objects.exists())
        mock_sms.assert_called_once()
        self.assertIn("critically low", mock_sms.call_args[0][0])


    def test_invalid_form_returns_error(self):
        form_data = {
            "date": date.today().isoformat(),
            "time": "11:00",
            # ❌ missing oxygen_purity
            "pressure": "5.0",
            "flow_rate": "10.0",
            "pdp": "-60.0",
        }
        response = self.client.post(reverse("daily_entry_form"), form_data)
        self.assertEqual(response.status_code, 200)  # re-render form
        self.assertContains(response, "⚠️ Please correct the errors below.")
