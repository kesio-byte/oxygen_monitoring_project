from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from daily_entries.models import DailyEntry


class TestAddEntryView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="kesio",
            password="password",
        )

        operator_group, _ = Group.objects.get_or_create(name="Operator")
        self.user.groups.add(operator_group)

        self.client.login(username="kesio", password="password")

    @patch("daily_entries.views.send_alert_email")
    def test_add_entry_triggers_sms_on_low_purity(self, mock_email):
        form_data = {
            "oxygen_purity": "85.0",
            "pressure": "5.0",
            "flow_rate": "10.0",
            "pdp": "-60.0",
        }
        response = self.client.post(reverse("daily_entry_form"), form_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(DailyEntry.objects.exists())
        mock_email.assert_called_once()
        self.assertIn("critically low", mock_email.call_args.args[0])

    def test_invalid_form_returns_error(self):
        form_data = {
            "date": date.today().isoformat(),
            "time": "11:00",
            # Missing oxygen_purity
            "pressure": "5.0",
            "flow_rate": "10.0",
            "pdp": "-60.0",
        }
        response = self.client.post(reverse("daily_entry_form"), form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please correct the errors below.")