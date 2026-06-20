from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Avg
from django.db.models.functions import ExtractWeek, ExtractYear
from daily_entries.forms import DailyEntryForm
from daily_entries.models import DailyEntry

def add_entry(request):
    form = DailyEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.operator = request.user
        entry.save()
        return redirect('weekly_dashboard')

    return render(request, 'daily_entries/entry_form.html', {
        'form': form,
        'today': timezone.now().date()
    })


def weekly_dashboard(request):
    weekly_data = (
        DailyEntry.objects
        .annotate(week=ExtractWeek('date'), year=ExtractYear('date'))
        .values('week', 'year')
        .annotate(
            avg_purity=Avg('oxygen_purity'),
            avg_pressure=Avg('pressure'),
            avg_flow_rate=Avg('flow_rate'),
            avg_pdp=Avg('pdp')
        )
        .order_by('year', 'week')
    )

    SAFE_PURITY = 93.0
    SAFE_PRESSURE = 4.5
    for week in weekly_data:
        alerts = []
        if week['avg_purity'] < SAFE_PURITY:
            alerts.append(f"Oxygen purity averaged {week['avg_purity']:.1f}% — below safe threshold.")
        if week['avg_pressure'] < SAFE_PRESSURE:
            alerts.append(f"Pressure averaged {week['avg_pressure']:.1f} bar — below safe threshold.")
        week['alerts'] = alerts
        week['label'] = f"Week {week['week']} ({week['year']})"

    return render(request, 'weekly_records/dashboard.html', {'weekly_data': weekly_data})


def weekly_dashboard(request):
    # Later you can query DailyEntry objects here
    # For now, just render a template
    return render(request, 'daily_entries/weekly_dashboard.html')
