from django.shortcuts import render

def homepage(request):
    return render(request, 'daily_entries/homepage.html')

