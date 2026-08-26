from django.db import migrations

def create_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Admin group → full permissions
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(Permission.objects.all())

    # Technician group → can view + change DailyEntry
    tech_group, _ = Group.objects.get_or_create(name="Technician")
    tech_perms = Permission.objects.filter(
        codename__in=["view_dailyentry", "change_dailyentry"]
    )
    tech_group.permissions.set(tech_perms)

    # Viewer group → can only view DailyEntry
    viewer_group, _ = Group.objects.get_or_create(name="Viewer")
    viewer_perms = Permission.objects.filter(codename="view_dailyentry")
    viewer_group.permissions.set(viewer_perms)

def remove_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Admin", "Technician", "Viewer"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("daily_entries", "0006_alter_dailyentry_operator"),  # ✅ depends on your last migration
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
