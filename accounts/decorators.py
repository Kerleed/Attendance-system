# accounts/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from .utils import is_admin, is_staff_member

def admin_required(view_func):
    """Restrict access to Admin users only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in first.")
            return redirect('login')
        if not is_admin(request.user):
            messages.error(request, "Access denied: Admins only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_required(view_func):
    """Restrict access to Staff users only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in first.")
            return redirect('login')
        if not is_staff_member(request.user):
            messages.error(request, "Access denied: Staff only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
