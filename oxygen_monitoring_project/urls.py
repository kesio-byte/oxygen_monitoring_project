from django.contrib import admin
from django.urls import path, include   # 👈 add include here
from core.views import homepage
from django.contrib.auth import views as auth_views

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

    # Weekly Records app 
    path('weekly_records/', include('weekly_records.urls')), 
    path('', homepage, name='homepage'),

]
