from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Create groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    tech_group, _ = Group.objects.get_or_create(name='Technician')
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

    # Get permissions for DailyEntry model specifically
    view_alert = Permission.objects.filter(
        codename='view_dailyentry',
        content_type__app_label='daily_entries'
    ).first()

    change_alert = Permission.objects.filter(
        codename='change_dailyentry',
        content_type__app_label='daily_entries'
    ).first()

    if not view_alert or not change_alert:
        return  # permissions not found yet

    # Assign permissions
    admin_group.permissions.set(Permission.objects.all())  # full access
    tech_group.permissions.set([view_alert, change_alert])
    viewer_group.permissions.set([view_alert])

def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Admin', 'Technician', 'Viewer']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("daily_entries", "0003_dailyentry_technician_ack"),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
