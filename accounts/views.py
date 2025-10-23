from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User


def login_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('home')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("attendance_home")  # redirect to your custom dashboard
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You’ve been logged out successfully.")
    return redirect("login")

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'accounts/register.html')