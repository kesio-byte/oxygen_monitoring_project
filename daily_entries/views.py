from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models import Avg
from .models import DailyEntry
from .forms import DailyEntryForm   # ✅ import the form here

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
    return render(request, 'daily_entries/entry_form.html', {'form': form})


def weekly_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    entries = DailyEntry.objects.filter(date__gte=week_start)

    # Aggregate averages for all key fields
    averages = entries.aggregate(
        purity=Avg("oxygen_purity"),
        pressure=Avg("pressure"),
        flow_rate=Avg("flow_rate"),
        pdp=Avg("pdp"),
    )

    context = {
        "entries": entries,
        "averages": averages,
    }
    return render(request, "daily_entries/weekly_dashboard.html", context)

