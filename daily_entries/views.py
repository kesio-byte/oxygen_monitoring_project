from datetime import timedelta
import json
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .email_utils import send_alert_email
from .forms import DailyEntryForm, CustomUserCreationForm
from .models import DailyEntry
from django.contrib.auth.views import LogoutView


# -------------------------
# Access control
# -------------------------
def operator_required(view_func):
    """Require the user to be logged in and belong to the Operator group."""
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.groups.filter(name="Operator").exists():
            messages.error(request, "Only Operators can submit daily entries.")
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapped


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
    users = User.objects.all().prefetch_related("groups")

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

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

        # Prevent an Admin from removing their own Admin role.
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
            "is_admin": True,
        },
    )


# -------------------------
# Daily Entries
# -------------------------
@operator_required
def add_entry(request):
    if request.method == "POST":
        form = DailyEntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.operator = request.user

            now = timezone.localtime(timezone.now())
            entry.date = now.date()
            entry.time = now.time().replace(second=0, microsecond=0)

            entry.save()

            if entry.oxygen_purity < 90:
                send_alert_email(
                    f"Oxygen purity critically low ({entry.oxygen_purity:.1f}%)"
                )
            elif entry.pressure < 4.0:
                send_alert_email(
                    f"Pressure critically low ({entry.pressure:.1f} bar)"
                )
            elif entry.flow_rate < 3.0:
                send_alert_email(
                    f"Flow rate critically low ({entry.flow_rate:.1f} L/min)"
                )
            elif entry.pdp > -50.0:
                send_alert_email(
                    f"PDP critically high ({entry.pdp:.1f} °C)"
                )

            messages.success(request, "Entry saved successfully.")
            return redirect("weekly_dashboard")

        messages.error(request, "Please correct the errors below.")
    else:
        form = DailyEntryForm()

    return render(
        request,
        "daily_entries/entry_form.html",
        {
            "form": form,
            "today": timezone.localtime(timezone.now()).date(),
        },
    )


# -------------------------
# Weekly Dashboard
# -------------------------
@login_required
def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=30)

    entries_qs = DailyEntry.objects.filter(
        date__gte=week_start
    ).order_by("-date", "-time")

    paginator = Paginator(entries_qs, 10)
    entries = paginator.get_page(request.GET.get("page"))

    aggregates = entries_qs.aggregate(
        avg_purity=Avg("oxygen_purity"),
        avg_pressure=Avg("pressure"),
        avg_flow=Avg("flow_rate"),
        avg_pdp=Avg("pdp"),
    )

    avg_purity = aggregates["avg_purity"]
    avg_pressure = aggregates["avg_pressure"]
    avg_flow = aggregates["avg_flow"]
    avg_pdp = aggregates["avg_pdp"]

    alerts = []

    if avg_purity is not None and avg_purity < 93.0:
        alerts.append(
            f"Oxygen purity averaged {avg_purity:.1f}% — below safe threshold."
        )

    if avg_pressure is not None and avg_pressure < 4.5:
        alerts.append(
            f"Pressure averaged {avg_pressure:.1f} bar — below safe threshold."
        )

    chart_entries = list(reversed(list(entries_qs)))
    labels_json = json.dumps([str(entry.date) for entry in chart_entries])
    purity_json = json.dumps(
        [float(entry.oxygen_purity) for entry in chart_entries]
    )
    pressure_json = json.dumps(
        [float(entry.pressure) for entry in chart_entries]
    )
    flow_json = json.dumps(
        [float(entry.flow_rate) for entry in chart_entries]
    )
    pdp_json = json.dumps([float(entry.pdp) for entry in chart_entries])

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


# -------------------------
# APIs
# -------------------------
def entries_api(request):
    entries = DailyEntry.objects.order_by("-date", "-time").values(
        "id",
        "date",
        "time",
        "operator",
        "oxygen_purity",
        "pressure",
        "flow_rate",
        "pdp",
    )
    return JsonResponse(list(entries), safe=False)


def monthly_api(request):
    today = timezone.now().date()
    month_start = today - timedelta(days=30)

    entries = (
        DailyEntry.objects.filter(date__gte=month_start)
        .select_related("operator")
        .order_by("-date")
    )

    data = [
        {
            "date": str(entry.date),
            "operator": entry.operator.username if entry.operator else "—",
            "oxygen_purity": float(entry.oxygen_purity),
            "pressure": float(entry.pressure),
            "flow_rate": float(entry.flow_rate),
            "pdp": float(entry.pdp),
        }
        for entry in entries
    ]

    return JsonResponse(data, safe=False)


def all_alerts_api(request):
    alerts = (
        DailyEntry.objects.select_related("operator")
        .order_by("-date", "-time")[:50]
    )

    data = [
        {
            "id": entry.id,
            "date": str(entry.date),
            "time": str(entry.time),
            "operator": entry.operator.username if entry.operator else "",
            "oxygen_purity": float(entry.oxygen_purity),
            "pressure": float(entry.pressure),
            "flow_rate": float(entry.flow_rate),
            "pdp": float(entry.pdp),
            "critical_flag": entry.critical_flag,
            "alert_status": entry.alert_status,
            "notes": entry.notes or "",
            "technician_ack": entry.technician_ack,
        }
        for entry in alerts
    ]

    return JsonResponse(data, safe=False)


def live_monitoring_api(request):
    latest = (
        DailyEntry.objects.select_related("operator")
        .order_by("-date", "-time")
        .first()
    )

    if not latest:
        return JsonResponse({"error": "No entries found"}, status=404)

    critical_flag = False
    alert_message = None

    if latest.oxygen_purity < 90:
        alert_message = (
            f"Oxygen purity critically low ({latest.oxygen_purity:.1f}%)"
        )
    elif latest.pressure < 4.0:
        alert_message = f"Pressure critically low ({latest.pressure:.1f} bar)"
    elif latest.flow_rate < 3.0:
        alert_message = (
            f"Flow rate critically low ({latest.flow_rate:.1f} L/min)"
        )
    elif latest.pdp > -50.0:
        alert_message = f"PDP critically high ({latest.pdp:.1f} °C)"

    critical_flag = alert_message is not None

    if critical_flag:
        try:
            send_mail(
                subject="Hospital Oxygen Monitoring Alert",
                message=alert_message,
                from_email=os.getenv("EMAIL_HOST_USER"),
                recipient_list=["kesiomtewacolllins@zohomail.com"],
                fail_silently=True,
            )
        except Exception as exc:
            print("Email error:", exc)

    return JsonResponse(
        {
            "date": str(latest.date),
            "time": str(latest.time),
            "operator": latest.operator.username if latest.operator else "—",
            "oxygen_purity": float(latest.oxygen_purity),
            "pressure": float(latest.pressure),
            "flow_rate": float(latest.flow_rate),
            "pdp": float(latest.pdp),
            "critical_flag": critical_flag,
            "email_sent": critical_flag,
        }
    )


# -------------------------
# Alerts
# -------------------------
@require_POST
def update_ack(request, entry_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to acknowledge alerts.")
        return redirect("login")

    entry = get_object_or_404(DailyEntry, id=entry_id)
    entry.technician_ack = request.POST.get("ack") == "true"
    entry.save(update_fields=["technician_ack"])

    messages.success(
        request,
        f"Alert {entry.id} acknowledgment set to {entry.technician_ack}.",
    )
    return redirect("alerts_page")


def unacknowledged_alerts(request):
    alerts = DailyEntry.objects.filter(
        technician_ack=False
    ).order_by("-date", "-time")

    return render(
        request,
        "daily_entries/unacknowledged_alerts.html",
        {"alerts": alerts},
    )


@login_required
def alerts_page(request):
    alert_history_qs = DailyEntry.objects.order_by("-date", "-time")
    paginator_all = Paginator(alert_history_qs, 10)
    alert_history = paginator_all.get_page(request.GET.get("page_all"))

    unack_qs = DailyEntry.objects.filter(
        alert_status=True,
        technician_ack=False,
    ).order_by("-date", "-time")

    paginator_unack = Paginator(unack_qs, 10)
    unack_alerts = paginator_unack.get_page(request.GET.get("page_unack"))

    return render(
        request,
        "daily_entries/alerts.html",
        {
            "alert_history": alert_history,
            "alerts": unack_alerts,
            "active_tab": request.GET.get("tab", "all"),
        },
    )


@login_required
@permission_required("daily_entries.change_dailyentry", raise_exception=True)
@require_POST
def alerts_ack(request, pk):
    entry = get_object_or_404(DailyEntry, pk=pk)
    entry.technician_ack = request.POST.get("ack") == "true"
    entry.save(update_fields=["technician_ack"])

    return JsonResponse(
        {
            "success": True,
            "ack": entry.technician_ack,
        }
    )


# -------------------------
# Other entry views
# -------------------------
def daily_entries_list(request):
    entries = DailyEntry.objects.all().order_by("-date", "-time")
    return render(request, "daily_entries/list.html", {"entries": entries})


# -------------------------
# Delete User (Admins only)
# -------------------------
@require_POST
@login_required
def delete_user(request):
    if not request.user.groups.filter(name="Admin").exists():
        messages.error(request, "Only Admins can delete users.")
        return redirect("users_list")

    user_id = request.POST.get("user_id")
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully.")

    return redirect("users_list")

def alerts_api(request):
    entries = DailyEntry.objects.order_by("-date", "-time")
    latest = entries.first()

    alert_messages = []
    if latest:
        if latest.oxygen_purity < 90:
            alert_messages.append(
                f"Latest oxygen purity critically low ({latest.oxygen_purity:.1f}%)"
            )
        if latest.pressure < 4.0:
            alert_messages.append(
                f"Latest pressure critically low ({latest.pressure:.1f} bar)"
            )
        if latest.flow_rate < 3.0:
            alert_messages.append(
                f"Latest flow rate critically low ({latest.flow_rate:.1f} L/min)"
            )
        if latest.pdp > -50.0:
            alert_messages.append(
                f"Latest PDP critically high ({latest.pdp:.1f} °C)"
            )

        if not alert_messages:
            alert_messages.append("System normal")

    alerts = [
        {"type": "latest", "message": message}
        for message in alert_messages
    ]

    # Keep the existing entry/pagination data expected by other API consumers.
    unack_qs = DailyEntry.objects.filter(
        alert_status=True,
        technician_ack=False,
    ).order_by("-date", "-time")

    paginator = Paginator(unack_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page_unack", 1))

    entry_data = [
        {
            "id": entry.id,
            "date": str(entry.date),
            "time": str(entry.time),
            "operator": entry.operator.username if entry.operator else "",
            "oxygen_purity": float(entry.oxygen_purity),
            "pressure": float(entry.pressure),
            "flow_rate": float(entry.flow_rate),
            "pdp": float(entry.pdp),
            "notes": entry.notes or "",
            "technician_ack": entry.technician_ack,
        }
        for entry in page_obj
    ]

    return JsonResponse({
        "alerts": alerts,
        "entries": entry_data,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "total_unack": paginator.count,
    })



class CustomLogoutView(LogoutView):
    next_page = "login"
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)