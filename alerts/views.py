from django.shortcuts import render
def weekly_dashboard(request):
    return render(request, 'daily_entries/weekly_dashboard.html')
