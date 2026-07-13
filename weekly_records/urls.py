from django.urls import path
from .views import weekly_dashboard

urlpatterns = [
    path('', weekly_dashboard, name='weekly_dashboard'),
]
