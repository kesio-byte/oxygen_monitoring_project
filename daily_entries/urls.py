# daily_entries/urls.py

from django.urls import path
from .views import add_entry, weekly_dashboard, entries_api, monthly_api  # 👈 include monthly_api here

urlpatterns = [
    path('', add_entry, name='daily_entry_form'),
    path('weekly/', weekly_dashboard, name='weekly_dashboard'),
    path('api/entries/', entries_api, name='entries_api'),
    path('api/monthly/', monthly_api, name='monthly_api'),  # 👈 now Django can find it
]
