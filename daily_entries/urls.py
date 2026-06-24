# daily_entries/urls.py

from django.urls import path
from .views import add_entry, weekly_dashboard, entries_api  # 👈 import the new view

urlpatterns = [
    path('', add_entry, name='daily_entry_form'),
    path('weekly/', weekly_dashboard, name='weekly_dashboard'),
    path('api/entries/', entries_api, name='entries_api'),  # 👈 new JSON endpoint
]
