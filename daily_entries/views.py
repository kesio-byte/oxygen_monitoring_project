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
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Avg


def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=7)

    # Order newest first
    entries_qs = DailyEntry.objects.filter(date__gte=week_start).order_by("-date")

    # Paginate: 10 entries per page
    paginator = Paginator(entries_qs, 10)
    page_number = request.GET.get("page")
    entries = paginator.get_page(page_number)

    # Calculate averages from full queryset
    avg_purity = entries_qs.aggregate(Avg("oxygen_purity"))["oxygen_purity__avg"]
    avg_pressure = entries_qs.aggregate(Avg("pressure"))["pressure__avg"]
    avg_flow = entries_qs.aggregate(Avg("flow_rate"))["flow_rate__avg"]
    avg_pdp = entries_qs.aggregate(Avg("pdp"))["pdp__avg"]

    SAFE_PURITY = 93.0
    SAFE_PRESSURE = 4.5
    alerts = []
    if avg_purity is not None and avg_purity < SAFE_PURITY:
        alerts.append(f"Oxygen purity averaged {avg_purity:.1f}% — below safe threshold.")
    if avg_pressure is not None and avg_pressure < SAFE_PRESSURE:
        alerts.append(f"Pressure averaged {avg_pressure:.1f} bar — below safe threshold.")

    labels_json = json.dumps([str(e.date) for e in entries_qs])
    purity_json = json.dumps([float(e.oxygen_purity) for e in entries_qs])
    pressure_json = json.dumps([float(e.pressure) for e in entries_qs])
    flow_json = json.dumps([float(e.flow_rate) for e in entries_qs])
    pdp_json = json.dumps([float(e.pdp) for e in entries_qs])

    context = {
        "entries": entries,  # paginated page object
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

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.operator = request.user
            entry.save()

            # If AJAX request, return JSON
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "entry": {
                        "date": str(entry.date),
                        "operator": entry.operator.username,
                        "oxygen_purity": entry.oxygen_purity,
                        "pressure": entry.pressure,
                        "flow_rate": entry.flow_rate,
                        "pdp": entry.pdp,
                    }
                })

            # Normal form submission
            messages.success(request, "✅ Entry saved successfully.")
            return redirect('weekly_dashboard')
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = DailyEntryForm()

    context = {
        'form': form,
        'today': timezone.now().date()
    }
    return render(request, 'daily_entries/entry_form.html', context)


def entries_api(request):
    entries = DailyEntry.objects.order_by("-date")[:50]
    data = [
        {
            "date": e.date,
            "operator": e.operator.username,
            "oxygen_purity": e.oxygen_purity,
            "pressure": e.pressure,
            "flow_rate": e.flow_rate,
            "pdp": e.pdp,
        }
        for e in entries
    ]
    return JsonResponse(data, safe=False)

def monthly_api(request):
    today = timezone.now().date()
    month_start = today - timedelta(days=30)

    entries = DailyEntry.objects.filter(date__gte=month_start).order_by("-date")

    data = [
        {
            "date": str(e.date),
            "operator": e.operator.username,
            "oxygen_purity": e.oxygen_purity,
            "pressure": e.pressure,
            "flow_rate": e.flow_rate,
            "pdp": e.pdp,
        }
        for e in entries
    ]
    return JsonResponse(data, safe=False)


def alerts_api(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    entries_qs = DailyEntry.objects.filter(date__gte=week_start)

    # Weekly averages
    avg_purity = entries_qs.aggregate(Avg("oxygen_purity"))["oxygen_purity__avg"]
    avg_pressure = entries_qs.aggregate(Avg("pressure"))["pressure__avg"]
    avg_flow = entries_qs.aggregate(Avg("flow_rate"))["flow_rate__avg"]
    avg_pdp = entries_qs.aggregate(Avg("pdp"))["pdp__avg"]

    # Latest entry
    latest = DailyEntry.objects.order_by("-date").first()

    # Thresholds
    SAFE_PURITY = 93.0
    CRITICAL_PURITY = 90.0
    SAFE_PRESSURE = 4.5
    CRITICAL_PRESSURE = 4.0
    SAFE_FLOW = 5.0
    CRITICAL_FLOW = 3.0
    SAFE_PDP = -55.0
    CRITICAL_PDP = -50.0

    alerts = []

    # --- Weekly trend alerts ---
    if avg_purity is not None and avg_purity < SAFE_PURITY:
        alerts.append({"level": "warning", "type": "trend", "message": f"⚠️ Weekly purity averaged {avg_purity:.1f}% — below safe threshold"})
    if avg_pressure is not None and avg_pressure < SAFE_PRESSURE:
        alerts.append({"level": "warning", "type": "trend", "message": f"⚠️ Weekly pressure averaged {avg_pressure:.1f} bar — below safe threshold"})
    if avg_flow is not None and avg_flow < SAFE_FLOW:
        alerts.append({"level": "warning", "type": "trend", "message": f"⚠️ Weekly flow averaged {avg_flow:.1f} L/min — below safe threshold"})
    if avg_pdp is not None and avg_pdp > SAFE_PDP:
        alerts.append({"level": "warning", "type": "trend", "message": f"⚠️ Weekly PDP averaged {avg_pdp:.1f} °C — above safe threshold"})

    # --- Latest entry alerts ---
    if latest:
        if latest.oxygen_purity < CRITICAL_PURITY:
            alerts.append({"level": "critical", "type": "latest", "message": f"❌ Latest purity critically low ({latest.oxygen_purity:.1f}%)"})
        elif latest.oxygen_purity < SAFE_PURITY:
            alerts.append({"level": "warning", "type": "latest", "message": f"⚠️ Latest purity below safe threshold ({latest.oxygen_purity:.1f}%)"})

        if latest.pressure < CRITICAL_PRESSURE:
            alerts.append({"level": "critical", "type": "latest", "message": f"❌ Latest pressure critically low ({latest.pressure:.1f} bar)"})
        elif latest.pressure < SAFE_PRESSURE:
            alerts.append({"level": "warning", "type": "latest", "message": f"⚠️ Latest pressure below safe threshold ({latest.pressure:.1f} bar)"})

        if latest.flow_rate < CRITICAL_FLOW:
            alerts.append({"level": "critical", "type": "latest", "message": f"❌ Latest flow rate critically low ({latest.flow_rate:.1f} L/min)"})
        elif latest.flow_rate < SAFE_FLOW:
            alerts.append({"level": "warning", "type": "latest", "message": f"⚠️ Latest flow rate below safe threshold ({latest.flow_rate:.1f} L/min)"})

        if latest.pdp > CRITICAL_PDP:
            alerts.append({"level": "critical", "type": "latest", "message": f"❌ Latest PDP critically high ({latest.pdp:.1f} °C)"})
        elif latest.pdp > SAFE_PDP:
            alerts.append({"level": "warning", "type": "latest", "message": f"⚠️ Latest PDP above safe threshold ({latest.pdp:.1f} °C)"})

    # Technician notification
    if alerts:
        alerts.append({"level": "info", "type": "system", "message": "✔️ SMS sent to technician"})

    return JsonResponse(alerts, safe=False)


def alerts_page(request):
    return render(request, "daily_entries/alerts.html")