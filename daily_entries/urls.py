from django.urls import path
from . import views

urlpatterns = [
    # Daily entries
    path('', views.add_entry, name='daily_entry_form'),
    path('weekly/', views.weekly_dashboard, name='weekly_dashboard'),
    path('api/entries/', views.entries_api, name='entries_api'),
    path('api/monthly/', views.monthly_api, name='monthly_api'),
    path('api/alerts/', views.alerts_api, name='alerts_api'),

    # Alerts
    path('alerts/', views.alerts_page, name='alerts_page'),
    path("alerts/ack/<int:entry_id>/", views.update_ack, name="update_ack"),
    path("unacknowledged/", views.unacknowledged_alerts, name="unacknowledged_alerts"),

    # User management (Admins only)
    path("users/", views.users_list, name="users_list"),
    path("users/<int:user_id>/roles/", views.manage_roles, name="manage_roles"),
    path("register/", views.register, name="register"),

    # Home
    path("home/", views.home, name="home"),
    # urls.py
    path("api/live/", views.live_monitoring_api, name="live_monitoring_api"),

]
