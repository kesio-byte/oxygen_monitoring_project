from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from .models import DailyEntry
import json
from django.contrib.auth.decorators import login_required, permission_required,user_passes_test
from django.contrib import messages
from .forms import DailyEntryForm
from django_tables2 import RequestConfig
from .tables import DailyEntryTable
from django.core.paginator import Paginator
from django.http import JsonResponse
from alerts.utils import  send_alert_email
from .models import DailyEntry
import os
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from . import views
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm

@login_required
def home(request):
     return render(request, "daily_entries/homepage.html")

@login_required
@permission_required("auth.add_user", raise_exception=True)
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("users_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "daily_entries/register.html", {"form": form})

@login_required
@permission_required("auth.change_user", raise_exception=True)
def manage_roles(request, user_id):
    user = get_object_or_404(User, id=user_id)
    groups = Group.objects.all()

    if request.method == "POST":
        selected_roles = request.POST.getlist("roles")
        user.groups.set(Group.objects.filter(id__in=selected_roles))
        messages.success(request, f"Roles updated for {user.username}.")
        return redirect("users_list")

    return render(request, "daily_entries/manage_roles.html", {"user": user, "groups": groups})

@require_POST
def update_ack(request, entry_id):
    try:
        entry = DailyEntry.objects.get(id=entry_id)
        ack_value = request.POST.get("ack") == "true"
        entry.technician_ack = ack_value
        entry.save()
        return JsonResponse({"success": True})
    except DailyEntry.DoesNotExist:
        return JsonResponse({"success": False, "error": "Entry not found"})

@login_required
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


@login_required
def add_entry(request):
    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.operator = request.user
            entry.save()

            # 🚨 Email trigger logic
            if entry.oxygen_purity < 90:
                send_alert_email(f"⚠️ Oxygen purity critically low ({entry.oxygen_purity:.1f}%)")
            elif entry.pressure < 4.0:
                send_alert_email(f"⚠️ Pressure critically low ({entry.pressure:.1f} bar)")
            elif entry.flow_rate < 3.0:
                send_alert_email(f"⚠️ Flow rate critically low ({entry.flow_rate:.1f} L/min)")
            elif entry.pdp > -50.0:
                send_alert_email(f"⚠️ PDP critically high ({entry.pdp:.1f} °C)")

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

            messages.success(request, "✅ Entry saved successfully.")
            return redirect('weekly_dashboard')
        else:
            # Handle invalid form
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
            messages.error(request, "⚠️ Please correct the errors below.")
            return render(request, 'daily_entries/entry_form.html', {"form": form, "today": timezone.now().date()})
    else:
        form = DailyEntryForm()

    context = {
        'form': form,
        'today': timezone.now().date()
    }
    return render(request, 'daily_entries/entry_form.html', context)

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

    avg_purity = entries_qs.aggregate(Avg("oxygen_purity"))["oxygen_purity__avg"]
    avg_pressure = entries_qs.aggregate(Avg("pressure"))["pressure__avg"]
    avg_flow = entries_qs.aggregate(Avg("flow_rate"))["flow_rate__avg"]
    avg_pdp = entries_qs.aggregate(Avg("pdp"))["pdp__avg"]

    latest = DailyEntry.objects.order_by("-date", "-time").first()

    SAFE_PURITY, CRITICAL_PURITY = 93.0, 90.0
    SAFE_PRESSURE, CRITICAL_PRESSURE = 4.5, 4.0
    SAFE_FLOW, CRITICAL_FLOW = 5.0, 3.0
    SAFE_PDP, CRITICAL_PDP = -55.0, -50.0

    trend_alerts = []
    if avg_purity is not None and avg_purity < SAFE_PURITY:
        trend_alerts.append({"level": "warning", "type": "trend",
                             "message": f"⚠️ Weekly purity averaged {avg_purity:.1f}% — below safe threshold"})
    if avg_pressure is not None and avg_pressure < SAFE_PRESSURE:
        trend_alerts.append({"level": "warning", "type": "trend",
                             "message": f"⚠️ Weekly pressure averaged {avg_pressure:.1f} bar — below safe threshold"})
    if avg_flow is not None and avg_flow < SAFE_FLOW:
        trend_alerts.append({"level": "warning", "type": "trend",
                             "message": f"⚠️ Weekly flow averaged {avg_flow:.1f} L/min — below safe threshold"})
    if avg_pdp is not None and avg_pdp > SAFE_PDP:
        trend_alerts.append({"level": "warning", "type": "trend",
                             "message": f"⚠️ Weekly PDP averaged {avg_pdp:.1f} °C — above safe threshold"})

    latest_alerts = []
    if latest:
        if latest.oxygen_purity < CRITICAL_PURITY:
            latest_alerts.append({"level": "critical", "type": "latest",
                                  "message": f"❌ Latest purity critically low ({latest.oxygen_purity:.1f}%)"})
        elif latest.oxygen_purity < SAFE_PURITY:
            latest_alerts.append({"level": "warning", "type": "latest",
                                  "message": f"⚠️ Latest purity below safe threshold ({latest.oxygen_purity:.1f}%)"})

        if latest.pressure < CRITICAL_PRESSURE:
            latest_alerts.append({"level": "critical", "type": "latest",
                                  "message": f"❌ Latest pressure critically low ({latest.pressure:.1f} bar)"})
        elif latest.pressure < SAFE_PRESSURE:
            latest_alerts.append({"level": "warning", "type": "latest",
                                  "message": f"⚠️ Latest pressure below safe threshold ({latest.pressure:.1f} bar)"})

        if latest.flow_rate < CRITICAL_FLOW:
            latest_alerts.append({"level": "critical", "type": "latest",
                                  "message": f"❌ Latest flow rate critically low ({latest.flow_rate:.1f} L/min)"})
        elif latest.flow_rate < SAFE_FLOW:
            latest_alerts.append({"level": "warning", "type": "latest",
                                  "message": f"⚠️ Latest flow rate below safe threshold ({latest.flow_rate:.1f} L/min)"})

        if latest.pdp > CRITICAL_PDP:
            latest_alerts.append({"level": "critical", "type": "latest",
                                  "message": f"❌ Latest PDP critically high ({latest.pdp:.1f} °C)"})
        elif latest.pdp > SAFE_PDP:
            latest_alerts.append({"level": "warning", "type": "latest",
                                  "message": f"⚠️ Latest PDP above safe threshold ({latest.pdp:.1f} °C)"})

        # ✅ Fallback applies only to latest alerts
        if not latest_alerts:
            latest_alerts.append({"level": "normal", "type": "latest",
                                  "message": "✔️ System normal — all readings within safe thresholds"})

    alerts = trend_alerts + latest_alerts

    if any(a["level"] in ["warning", "critical"] for a in latest_alerts):
        alerts.append({"level": "info", "type": "system",
                       "message": "✔️ Email sent to technician"})

    return JsonResponse(alerts, safe=False)

@login_required
def alerts_page(request):
    # Latest 20 entries, newest first
    alert_history = DailyEntry.objects.order_by('-date', '-time')[:20]
    technician_email = os.getenv("TECHNICIAN_EMAIL")
    return render(request, "daily_entries/alerts.html", {
        "alert_history": alert_history,
        "technician_email": technician_email,
    })

@login_required
def alerts_view(request):
    technician_email = os.getenv("TECHNICIAN_EMAIL")
    alert_history = DailyEntry.objects.all().order_by('-date', '-time')
    return render(request, "daily_entries/alerts.html", {
        "alert_history": alert_history,
        "technician_email": technician_email,
    })


@login_required
def live_monitoring(request):
    # Everyone logged in can see
    return render(request, "daily_entries/live.html")

def all_alerts(request):
    # Viewer, Technician, Admin
    return render(request, "daily_entries/all.html")

@permission_required('daily_entries.change_dailyentry', raise_exception=True)
def unacknowledged_alerts(request):
    # Technician + Admin only
    return render(request, "daily_entries/unack.html")

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url="login", redirect_field_name=None)
def users_list(request):
    query = request.GET.get("q")
    users = User.objects.all()
    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )
    return render(request, "daily_entries/users.html", {"users": users})
