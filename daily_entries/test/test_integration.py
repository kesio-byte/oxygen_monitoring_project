from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from daily_entries.models import DailyEntry


class TestIntegrationWorkflow(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="kesio",
            password="password",
        )
        self.client.login(username="kesio", password="password")

    def test_faulty_and_normal_entries_in_alerts_api(self):
        faulty_entry = DailyEntry.objects.create(
            operator=self.user,
            date=date.today(),
            time=time(8, 0),
            oxygen_purity=95.0,
            pressure=3.0,
            flow_rate=-75.0,
            pdp=-60.0,
           
        )

        # This is the latest entry, so the API should report "System normal".
        DailyEntry.objects.create(
            operator=self.user,
            date=date.today(),
            time=time(9, 0),
            oxygen_purity=95.0,
            pressure=5.0,
            flow_rate=10.0,
            pdp=-60.0,
        )

        response = self.client.get(reverse("alerts_api"))
        latest_messages = [alert["message"] for alert in response.json()["alerts"]]
        self.assertEqual(latest_messages, ["System normal"])