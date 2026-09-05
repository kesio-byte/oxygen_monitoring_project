from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
import json, os
from django.core.mail import send_mail
from .models import DailyEntry
from .forms import DailyEntryForm, CustomUserCreationForm
from alerts.utils import send_alert_email

# -------------------------
# Home Page
# -------------------------
@login_required
def home(request):
    return render(request, "daily_entries/homepage.html")

# -------------------------
# User List (Admins only)
# -------------------------
@login_required
def users_list(request):
    if not request.user.groups.filter(name="Admin").exists():
        messages.error(request, "Only Admins can view the user list.")
        return redirect("home")

    query = request.GET.get("q")
    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    return render(request, "daily_entries/users.html", {"users": users})

# -------------------------
# Register New User (Admins only)
# -------------------------
@login_required
def register(request):
    if not request.user.groups.filter(name="Admin").exists():
        messages.error(request, "Only Admins can create new accounts.")
        return redirect("users_list")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("users_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "daily_entries/register.html", {"form": form})

# -------------------------
# Manage Roles (Admins only)
# -------------------------
@login_required
def manage_roles(request, user_id):
    if not request.user.groups.filter(name="Admin").exists():
        messages.error(request, "Only Admins can manage roles.")
        return redirect("users_list")

    user = get_object_or_404(User, id=user_id)
    groups = Group.objects.all()

    if request.method == "POST":
        selected_roles = request.POST.getlist("roles")
        selected_groups = Group.objects.filter(id__in=selected_roles)

        # 🚨 Safeguard: prevent removing your own Admin role
        if user == request.user and not selected_groups.filter(name="Admin").exists():
            messages.error(request, "You cannot remove your own Admin role.")
            return redirect("manage_roles", user_id=user.id)

        user.groups.set(selected_groups)
        messages.success(request, f"Roles updated for {user.username}.")
        return redirect("users_list")

    return render(
        request,
        "daily_entries/manage_roles.html",
        {
            "user": user,
            "groups": groups,
            "is_admin": request.user.groups.filter(name="Admin").exists(),
        },
    )

# -------------------------
# Daily Entries
# -------------------------
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

            messages.success(request, "✅ Entry saved successfully.")
            return redirect('weekly_dashboard')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = DailyEntryForm()

    return render(request, 'daily_entries/entry_form.html', {"form": form, "today": timezone.now().date()})

# -------------------------
# Weekly Dashboard
# -------------------------
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

    SAFE_PURITY, SAFE_PRESSURE = 93.0, 4.5
    alerts = []
    if avg_purity and avg_purity < SAFE_PURITY:
        alerts.append(f"Oxygen purity averaged {avg_purity:.1f}% — below safe threshold.")
    if avg_pressure and avg_pressure < SAFE_PRESSURE:
        alerts.append(f"Pressure averaged {avg_pressure:.1f} bar — below safe threshold.")

    context = {
        "entries": entries,
        "avg_purity": avg_purity,
        "avg_pressure": avg_pressure,
        "avg_flow": avg_flow,
        "avg_pdp": avg_pdp,
        "alerts": alerts,
    }
    return render(request, "daily_entries/weekly_dashboard.html", context)

# -------------------------
# Alerts
# -------------------------
@login_required
def alerts_page(request):
    alert_history = DailyEntry.objects.order_by('-date', '-time')[:20]
    technician_email = os.getenv("TECHNICIAN_EMAIL")
    return render(request, "daily_entries/alerts.html", {
        "alert_history": alert_history,
        "technician_email": technician_email,
    })


def entries_api(request):
    # Example: return all entries as JSON
    entries = DailyEntry.objects.all().values(
        "id", "date", "time", "operator",
        "oxygen_purity", "pressure", "flow_rate", "pdp"
    )
    return JsonResponse(list(entries), safe=False)


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
    # Example: return only critical/warning alerts
    alerts = DailyEntry.objects.filter(
        critical_flag=True
    ) | DailyEntry.objects.filter(alert_status=True)

    data = [
        {
            "id": e.id,
            "date": str(e.date),
            "time": str(e.time),
            "operator": e.operator.username if e.operator else "",
            "oxygen_purity": e.oxygen_purity,
            "pressure": e.pressure,
            "flow_rate": e.flow_rate,
            "pdp": e.pdp,
            "critical_flag": e.critical_flag,
            "alert_status": e.alert_status,
            "notes": e.notes,
        }
        for e in alerts.order_by("-date", "-time")[:20]  # latest 20 alerts
    ]
    return JsonResponse(data, safe=False)


def update_ack(request, entry_id):
    entry = get_object_or_404(DailyEntry, id=entry_id)

    # Only allow authenticated users to acknowledge
    if request.user.is_authenticated:
        entry.alert_status = False   # or set an "acknowledged" flag if you have one
        entry.save()
        messages.success(request, f"Alert for entry {entry.id} acknowledged.")
    else:
        messages.error(request, "You must be logged in to acknowledge alerts.")

    return redirect("alerts_page")  # redirect back to alerts page



def unacknowledged_alerts(request):
    # Filter entries where alert_status is True (still active)
    alerts = DailyEntry.objects.filter(alert_status=True).order_by("-date", "-time")

    return render(
        request,
        "daily_entries/unacknowledged_alerts.html",
        {"alerts": alerts}
    )

def alerts_page(request):
    alert_history = DailyEntry.objects.order_by("-date", "-time")[:50]
    return render(request, "daily_entries/alerts.html", {"alert_history": alert_history})


def live_monitoring_api(request):
    latest = DailyEntry.objects.order_by("-date", "-time").first()
    if not latest:
        return JsonResponse({"error": "No entries found"})

    critical_flag = False
    alert_message = None

    if latest.oxygen_purity < 90:
        alert_message = f"⚠️ Oxygen purity critically low ({latest.oxygen_purity:.1f}%)"
        critical_flag = True
    elif latest.pressure < 4.0:
        alert_message = f"⚠️ Pressure critically low ({latest.pressure:.1f} bar)"
        critical_flag = True
    elif latest.flow_rate < 3.0:
        alert_message = f"⚠️ Flow rate critically low ({latest.flow_rate:.1f} L/min)"
        critical_flag = True
    elif latest.pdp > -50.0:
        alert_message = f"⚠️ PDP critically high ({latest.pdp:.1f} °C)"
        critical_flag = True

    # 🚨 Try sending email but don’t block JSON
    if critical_flag and alert_message:
        try:
            send_mail(
                subject="Hospital Oxygen Monitoring Alert",
                message=alert_message,
                from_email=os.getenv("EMAIL_HOST_USER"),
                recipient_list=["technician@example.com"],
                fail_silently=False,
            )
        except Exception as e:
            print("Email error:", e)
    return JsonResponse({
        "date": str(latest.date),
        "time": str(latest.time),
        "operator": latest.operator.username if latest.operator else "—",
        "oxygen_purity": latest.oxygen_purity,
        "pressure": latest.pressure,
        "flow_rate": latest.flow_rate,
        "pdp": latest.pdp,
        "critical_flag": critical_flag,
        "email_sent": True if (critical_flag and alert_message) else False,
})

