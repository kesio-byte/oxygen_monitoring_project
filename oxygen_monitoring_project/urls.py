# oxygen_monitoring_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from daily_entries.views import (
    home,
    alerts_page,
    users_list,
    CustomLogoutView,
)

#----------------------- URL Patterns ----------------------
urlpatterns = [

    # Admin and Authentication URLs
    path("admin/", admin.site.urls),
    path("", home, name="home"),

    # Login URL using Django's built-in LoginView with a custom template
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    # Logout URL using the custom logout view
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    # Password reset URLs
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    # Password reset done and complete URLs
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Include the daily_entries app URLs
    path("daily_entries/", include("daily_entries.urls")),
    path("alerts/", alerts_page, name="alerts_page"),
    path("users/", users_list, name="users_list"),
]