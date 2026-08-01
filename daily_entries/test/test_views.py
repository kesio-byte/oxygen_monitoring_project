import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from daily_entries.models import DailyEntry
from daily_entries.views import alerts_api

class TestAlertsApi(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="kesio")

    def test_alerts_api_flips_from_faulty_to_normal(self):
        # Faulty entry
        DailyEntry.objects.create(
            operator=self.user,
            oxygen_purity=92.0,
            pressure=3.0,
            flow_rate=-78.0,
            pdp=-50.0
        )
        request = self.factory.get("/daily_entries/api/alerts/")
        response = alerts_api(request)
        data = json.loads(response.content.decode())
        latest_messages = [a["message"] for a in data if a["type"] == "latest"]
        self.assertTrue(any("Latest pressure critically low" in m for m in latest_messages))
        self.assertTrue(any("Latest flow rate critically low" in m for m in latest_messages))

        # Healthy entry
        DailyEntry.objects.create(
            operator=self.user,
            oxygen_purity=97.0,
            pressure=8.0,
            flow_rate=55.0,
            pdp=-64.0
        )
        request = self.factory.get("/daily_entries/api/alerts/")
        response = alerts_api(request)
        data = json.loads(response.content.decode())
        latest_messages = [a["message"] for a in data if a["type"] == "latest"]
        self.assertTrue(any("System normal" in m for m in latest_messages))

