from django.contrib.auth.models import Group

def admin_status(request):
    return {
        "is_admin": request.user.is_authenticated and 
                    request.user.groups.filter(name="Admin").exists()
    }
