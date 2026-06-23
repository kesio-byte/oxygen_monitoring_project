# The Daily_entries weekly_dashboard view retrieves daily entries for the last 7 days, 
# calculates averages for oxygen purity, pressure, flow rate, 
# and PDP, checks against safety thresholds, 
# and prepares data for rendering in a template with Chart.js visualizations.

from django.shortcuts import render,redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from .models import DailyEntry
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DailyEntryForm
from django_tables2 import RequestConfig
from .tables import DailyEntryTable

def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=7)  # last 7 days
    entries = DailyEntry.objects.filter(date__gte=week_start).order_by("date")

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
from django.utils import timezone

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.operator = request.user
            entry.save()
            messages.success(request, "✅ Entry saved successfully.")
            return redirect('homepage')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = DailyEntryForm()

    context = {
        'form': form,
        'today': timezone.now().date()  # 👈 add this
    }
    return render(request, 'daily_entries/entry_form.html', context)


