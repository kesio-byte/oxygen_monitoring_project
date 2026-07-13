import django_tables2 as tables
from .models import DailyEntry

class DailyEntryTable(tables.Table):
    class Meta:
        model = DailyEntry
        fields = ("date", "operator", "oxygen_purity", "pressure", "flow_rate", "pdp")
        template_name = "django_tables2/table.html"  # you can override with Tailwind
