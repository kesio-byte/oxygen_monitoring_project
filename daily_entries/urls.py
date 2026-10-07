# My daily- entries urls.py files

from django.urls import path
from . import views

urlpatterns = [
    # Daily entries urls
    path('', views.add_entry, name='daily_entry_form'),
    path('weekly/', views.weekly_dashboard, name='weekly_dashboard'),
    path('api/entries/', views.entries_api, name='entries_api'),
    path('api/monthly/', views.monthly_api, name='monthly_api'),

    # Alerts APIs ulrs
    path('api/alerts/', views.alerts_api, name='alerts_api'),              # unack only
    path('api/all_alerts/', views.all_alerts_api, name='all_alerts_api'),  # new route

    # Alerts pages urls
    path('alerts/', views.alerts_page, name='alerts_page'),
   # path("alerts/ack/<int:entry_id>/", views.update_ack, name="update_ack"),
    path("unacknowledged/", views.unacknowledged_alerts, name="unacknowledged_alerts"),

    # User management urls
    path("users/", views.users_list, name="users_list"),
    path("users/<int:user_id>/roles/", views.manage_roles, name="manage_roles"),
    path("register/", views.register, name="register"),

    # Roles CRUD urls
  
    path("users/delete/", views.delete_user, name="delete_user"),


    # Home urls
    path("home/", views.home, name="home"),

    # Live monitoring urls
    path("api/live/", views.live_monitoring_api, name="live_monitoring_api"),

    # Acknowledgment urls
    path("alerts/ack/<int:pk>/", views.alerts_ack, name="alerts_ack"),

    # End of urls
]
