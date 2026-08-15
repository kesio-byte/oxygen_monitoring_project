from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from daily_entries.models import DailyEntry
from datetime import date, time

class PermissionTests(TestCase):
    def setUp(self):
        # Permissions
        change_perm = Permission.objects.get(codename="change_dailyentry")
        view_perm = Permission.objects.get(codename="view_dailyentry")

        # Groups
        self.admin_group = Group.objects.create(name="Admin")
        self.tech_group = Group.objects.create(name="Technician")
        self.viewer_group = Group.objects.create(name="Viewer")

        # Assign permissions
        self.admin_group.permissions.add(change_perm, view_perm)
        self.tech_group.permissions.add(change_perm, view_perm)
        self.viewer_group.permissions.add(view_perm)

        # Users
        self.admin = User.objects.create_user("admin", password="pass123")
        self.admin.groups.add(self.admin_group)

        self.tech = User.objects.create_user("tech", password="pass123")
        self.tech.groups.add(self.tech_group)

        self.viewer = User.objects.create_user("viewer", password="pass123")
        self.viewer.groups.add(self.viewer_group)

        # Dummy DailyEntry
        self.entry = DailyEntry.objects.create(
            operator="Tester",  # adjust if FK to User
            date=date.today(),
            time=time(10, 0),
            oxygen_purity=95.0,
            pressure=5.0,
            flow_rate=10.0,
            pdp=2.0,
            critical_flag=True,
            alert_status=True,
        )
        
def test_viewer_cannot_acknowledge(self):
    self.client.login(username="viewer", password="pass123")
    response = self.client.post(reverse("unacknowledged_alerts"), {"pk": self.entry.pk, "ack": True})
    self.assertEqual(response.status_code, 403)

def test_technician_can_acknowledge(self):
    self.client.login(username="tech", password="pass123")
    response = self.client.post(reverse("unacknowledged_alerts"), {"pk": self.entry.pk, "ack": True})
    self.assertNotEqual(response.status_code, 403)
    self.entry.refresh_from_db()
    self.assertTrue(self.entry.technician_ack)

def test_admin_can_acknowledge(self):
    self.client.login(username="admin", password="pass123")
    response = self.client.post(reverse("unacknowledged_alerts"), {"pk": self.entry.pk, "ack": True})
    self.assertNotEqual(response.status_code, 403)
    self.entry.refresh_from_db()
    self.assertTrue(self.entry.technician_ack)
