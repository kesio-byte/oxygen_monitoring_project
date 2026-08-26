from django.contrib.auth.views import LogoutView
from django.shortcuts import render

def homepage(request):
    return render(request, 'daily_entries/homepage.html')

class CustomLogoutView(LogoutView):
    next_page = "login"

    # explicitly allow GET requests
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        # Treat GET like POST
        return super().post(request, *args, **kwargs)
