import json
from datetime import date, time

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from daily_entries.models import DailyEntry
from daily_entries.views import alerts_api


class TestAlertsApi(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="kesio")

    def test_alerts_api_flips_from_faulty_to_normal(self):
        today = date.today()

        DailyEntry.objects.create(
            operator=self.user,
            date=today,
            time=time(8, 0),
            oxygen_purity=92.0,
            pressure=3.0,
            flow_rate=-78.0,
            pdp=-50.0,
        )

        response = alerts_api(
            self.factory.get("/daily_entries/api/alerts/")
        )
        data = json.loads(response.content.decode())

        latest_messages = [
            alert["message"]
            for alert in data["alerts"]
            if alert["type"] == "latest"
        ]
        self.assertTrue(any(
            "Latest pressure critically low" in message
            for message in latest_messages
        ))
        self.assertTrue(any(
            "Latest flow rate critically low" in message
            for message in latest_messages
        ))

        DailyEntry.objects.create(
            operator=self.user,
            date=today,
            time=time(9, 0),
            oxygen_purity=97.0,
            pressure=8.0,
            flow_rate=55.0,
            pdp=-64.0,
        )

        response = alerts_api(
            self.factory.get("/daily_entries/api/alerts/")
        )
        data = json.loads(response.content.decode())

        latest_messages = [
            alert["message"]
            for alert in data["alerts"]
            if alert["type"] == "latest"
        ]
        self.assertIn("System normal", latest_messages)