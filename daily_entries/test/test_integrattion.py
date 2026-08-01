from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from daily_entries.models import DailyEntry
from datetime import date, time
import json

class TestIntegrationWorkflow(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="kesio", password="password")
        self.client.login(username="kesio", password="password")

    def test_faulty_then_normal_entry_alerts(self):
        # 1️⃣ Add faulty entry (low pressure)
        DailyEntry.objects.create(
            operator=self.user,
            date=date.today(),
            time=time(8, 0),
            oxygen_purity=95.0,
            pressure=3.0,   # ❌ critical low
            flow_rate=10.0,
            pdp=-60.0
        )

        response = self.client.get(reverse("alerts_api"))
        data = json.loads(response.content.decode())
        latest_messages = [a["message"] for a in data if a["type"] == "latest"]
        self.assertTrue(any("Latest pressure critically low" in m for m in latest_messages))

        # 2️⃣ Add healthy entry (safe values)
        DailyEntry.objects.create(
            operator=self.user,
            date=date.today(),
            time=time(9, 0),
            oxygen_purity=95.0,
            pressure=5.0,
            flow_rate=10.0,
            pdp=-60.0
        )

        response = self.client.get(reverse("alerts_api"))
        data = json.loads(response.content.decode())
        latest_messages = [a["message"] for a in data if a["type"] == "latest"]
        self.assertTrue(any("System normal" in m for m in latest_messages))
