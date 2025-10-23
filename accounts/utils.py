from django.contrib.auth.decorators import user_passes_test

# Existing functions
from django.contrib.auth.models import Group

def is_admin(user):
    """Check if user belongs to Admin group."""
    return user.groups.filter(name="Admin").exists()

def is_staff_member(user):
    """Check if user belongs to Staff group."""
    return user.groups.filter(name="Staff").exists()


# New decorators
def admin_required(view_func):
    """Allow only users in the Admin group."""
    return user_passes_test(is_admin)(view_func)

def staff_required(view_func):
    """Allow only users in the Staff group."""
    return user_passes_test(is_staff_member)(view_func)