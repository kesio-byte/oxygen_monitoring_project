
from django.shortcuts import render,redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from .models import DailyEntry
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django_tables2 import RequestConfig

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Avg

def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=7)

    entries_qs = DailyEntry.objects.filter(date__gte=week_start).order_by("-date")

    paginator = Paginator(entries_qs, 10)
    page_number = request.GET.get("page")
    entries = paginator.get_page(page_number)

    avg_purity = entries_qs.aggregate(Avg("oxygen_purity"))["oxygen_purity__avg"]
    avg_pressure = entries_qs.aggregate(Avg("pressure"))["pressure__avg"]
    avg_flow = entries_qs.aggregate(Avg("flow_rate"))["flow_rate__avg"]
    avg_pdp = entries_qs.aggregate(Avg("pdp"))["pdp__avg"]

    alerts = []
    if avg_purity is not None and avg_purity < 93.0:
        alerts.append(f"⚠️ Oxygen purity averaged {avg_purity:.1f}% — below safe threshold.")
    if avg_pressure is not None and avg_pressure < 4.5:
        alerts.append(f"⚠️ Pressure averaged {avg_pressure:.1f} bar — below safe threshold.")

    labels_json = json.dumps([str(e.date) for e in entries_qs])
    purity_json = json.dumps([float(e.oxygen_purity) for e in entries_qs])
    pressure_json = json.dumps([float(e.pressure) for e in entries_qs])
    flow_json = json.dumps([float(e.flow_rate) for e in entries_qs])
    pdp_json = json.dumps([float(e.pdp) for e in entries_qs])

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
