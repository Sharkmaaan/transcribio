from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

# Create your views here.

# accounts/views.py

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def check_verification_status(request):
    """Check if user's email is verified"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user
        # Check if user has a verified email
        is_verified = user.emailaddress_set.filter(verified=True).exists()
        return JsonResponse({'verified': is_verified})
    return JsonResponse({'error': 'Invalid request'}, status=400)