# daily_entries/urls.py

from django.urls import path
from .views import (
    add_entry,
    weekly_dashboard,
    entries_api,
    monthly_api,
    alerts_api,
    alerts_page,
)

urlpatterns = [
    path('', add_entry, name='daily_entry_form'),
    path('weekly/', weekly_dashboard, name='weekly_dashboard'),
    path('api/entries/', entries_api, name='entries_api'),
    path('api/monthly/', monthly_api, name='monthly_api'),   # ✅ monthly API
    path('api/alerts/', alerts_api, name='alerts_api'),      # ✅ alerts API
    path('alerts/', alerts_page, name='alerts_page'),        # ✅ alerts page
]
