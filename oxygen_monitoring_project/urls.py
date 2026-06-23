#oxygen_monitoring_project/urls.py
from django.contrib import admin
from django.urls import path, include
from core.views import homepage
from django.contrib.auth import views as auth_views
from daily_entries.views import weekly_dashboard   # ✅ import here

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Homepage
    path('', homepage, name='homepage'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Daily Entries app
    path('daily_entries/', include('daily_entries.urls')),

    # Weekly Records page (points to unified view)
    path('weekly_records/', weekly_dashboard, name='weekly_records'),
]
