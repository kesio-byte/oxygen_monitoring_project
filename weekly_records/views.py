
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from .models import DailyEntry
import json
from django.conf import settings

def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=30)  # last 30 days
    entries = DailyEntry.objects.filter(date__gte=week_start).order_by("date")

    print(entries.count())
    print("DB path:", settings.DATABASES['default']['NAME'])
    print("WEEKLY DASHBOARD VIEW LOADED")

    # Calculate averages
    avg_purity = entries.aggregate(Avg("oxygen_purity"))["oxygen_purity__avg"]
    avg_pressure = entries.aggregate(Avg("pressure"))["pressure__avg"]
    avg_flow = entries.aggregate(Avg("flow_rate"))["flow_rate__avg"]
    avg_pdp = entries.aggregate(Avg("pdp"))["pdp__avg"]

    # Safety thresholds
    SAFE_PURITY = 93.0
    SAFE_PRESSURE = 4.5
    alerts = []
    if avg_purity is not None and avg_purity < SAFE_PURITY:
        alerts.append(f"Oxygen purity averaged {avg_purity:.1f}% — below safe threshold.")
    if avg_pressure is not None and avg_pressure < SAFE_PRESSURE:
        alerts.append(f"Pressure averaged {avg_pressure:.1f} bar — below safe threshold.")

    # Prepare JSON arrays for Chart.js
    labels_json = json.dumps([str(e.date) for e in entries])
    purity_json = json.dumps([float(e.oxygen_purity) for e in entries])
    pressure_json = json.dumps([float(e.pressure) for e in entries])
    flow_json = json.dumps([float(e.flow_rate) for e in entries])
    pdp_json = json.dumps([float(e.pdp) for e in entries])

    context = {
        "entries": entries,
        "avg_purity": avg_purity,
        "avg_pressure": avg_pressure,
        "avg_flow": avg_flow,
        "avg_pdp": avg_pdp,
        "alerts": alerts,
        "labels_json": labels_json,
        "purity_json": purity_json,
        "pressure_json": pressure_json,
        "flow_json": flow_json,
        "pdp_json": pdp_json,
    }
    return render(request, "daily_entries/weekly_dashboard.html", context)
