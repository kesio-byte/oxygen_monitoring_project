# daily_entries/migrations/0002_seed_groups.py
from django.db import migrations

def seed_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Admin group
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(Permission.objects.filter(codename__in=["add_user", "change_user"]))

    # Technician group
    technician_group, _ = Group.objects.get_or_create(name="Technician")
    technician_group.permissions.set(Permission.objects.filter(codename__in=["change_dailyentry"]))

    # Viewer group
    viewer_group, _ = Group.objects.get_or_create(name="Viewer")
    viewer_group.permissions.set(Permission.objects.filter(codename__in=["view_dailyentry"]))

def unseed_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Admin", "Technician", "Viewer"]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("daily_entries", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(seed_groups, unseed_groups),
    ]
