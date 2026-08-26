from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from daily_entries.views import home, weekly_dashboard, alerts_page, users_list
from core.views import CustomLogoutView   # keep your custom logout view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Homepage (protected)
    path('', home, name='homepage'),   # ✅ uses @login_required view in daily_entries/views.py

    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Password reset flow
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Apps
    path('daily_entries/', include('daily_entries.urls')),
    path('weekly_records/', weekly_dashboard, name='weekly_records'),
    path('alerts/', alerts_page, name='alerts_page'),
    path('users/', users_list, name='users_list'),
]
