import json

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from daily_entries.models import DailyEntry
from daily_entries.views import alerts_api


class TestAlertsApi(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="kesio")

    def get_alerts(self):
        request = self.factory.get("/daily_entries/api/alerts/")
        response = alerts_api(request)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content.decode())

    def test_alerts_api_returns_entries(self):
        DailyEntry.objects.create(
            operator=self.user,
            oxygen_purity=92.0,
            pressure=3.0,
            flow_rate=-78.0,
            pdp=-50.0,
        )

        data = self.get_alerts()

        self.assertIn("alerts", data)
        self.assertEqual(len(data["alerts"]), 2)

        messages = [alert["message"] for alert in data["alerts"]]
        self.assertIn("Latest pressure critically low (3.0 bar)", messages)
        self.assertIn("Latest flow rate critically low (-78.0 L/min)", messages)    