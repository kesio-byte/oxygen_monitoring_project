from django.test import SimpleTestCase
from django.urls import reverse, resolve
from daily_entries import views

class TestUrls(SimpleTestCase):

    def test_weekly_dashboard_url(self):
        url = reverse("weekly_dashboard")
        self.assertEqual(resolve(url).func, views.weekly_dashboard)

    def test_daily_entry_form_url(self):
        url = reverse("daily_entry_form")   # matches your urls.py
        self.assertEqual(resolve(url).func, views.add_entry)

    def test_entries_api_url(self):
        url = reverse("entries_api")
        self.assertEqual(resolve(url).func, views.entries_api)

    def test_alerts_api_url(self):
        url = reverse("alerts_api")
        self.assertEqual(resolve(url).func, views.alerts_api)

    def test_alerts_page_url(self):
        url = reverse("alerts_page")
        self.assertEqual(resolve(url).func, views.alerts_page)

    def test_monthly_api_url(self):
        url = reverse("monthly_api")
        self.assertEqual(resolve(url).func, views.monthly_api)
