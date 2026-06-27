# daily_entries/urls.py

from django.urls import path
<<<<<<< HEAD
from .views import add_entry, weekly_dashboard
=======
from .views import add_entry, weekly_dashboard, entries_api, monthly_api, alerts_api, alerts_page


>>>>>>> 39c4455 (Implement three-stage alerts model and dashboard integration)

urlpatterns = [
    path('', add_entry, name='daily_entry_form'),
    path('weekly/', weekly_dashboard, name='weekly_dashboard'),
<<<<<<< HEAD
=======
    path('api/entries/', entries_api, name='entries_api'),
    path('api/monthly/', monthly_api, name='monthly_api'),  # 👈 now Django can find it
    path('api/alerts/', alerts_api, name='alerts_api'),  # 👈 new route
    path('alerts/', alerts_page, name='alerts_page'),   # 👈 new route
>>>>>>> 39c4455 (Implement three-stage alerts model and dashboard integration)
]
