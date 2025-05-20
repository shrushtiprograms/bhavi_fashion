from .models import TailorApplication

def tailor_application_status(request):
    context = {}
    if request.user.is_authenticated:
        context['has_tailor_application'] = TailorApplication.objects.filter(user=request.user).exists()
    return context