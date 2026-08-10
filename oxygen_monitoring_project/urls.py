#oxygen_monitoring_project/urls.py
from django.contrib import admin
from django.urls import path, include
from core.views import homepage
from django.contrib.auth import views as auth_views
from daily_entries.views import weekly_dashboard   # ✅ import here

from daily_entries.views import alerts_page   # import the view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('daily_entries/', include('daily_entries.urls')),
    path('weekly_records/', weekly_dashboard, name='weekly_records'),
    path('alerts/', alerts_page, name='alerts_page'),  # 👈 shortcut
]
