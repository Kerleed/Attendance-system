from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm, AttendanceForm
from django.http import HttpResponse
from .models import Task, Attendance, Staff
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta, datetime
from django.contrib.auth.decorators import login_required
from accounts.utils import admin_required, staff_required

@login_required
@staff_required
def home(request):
    return render(request, 'attendance/home.html')

@staff_required
def dashboard(request):
    # gather simple stats for admin dashboard
    today = timezone.now().date()
    attendance_today = Attendance.objects.filter(date=today)
    total_staff = Staff.objects.count()
    present_staff = attendance_today.count()
    absent_staff = total_staff - present_staff

    total_hours_worked = attendance_today.aggregate(total=Sum('hours_worked'))['total'] or 0
    late_staff = attendance_today.filter(is_late=True).count()
    early_leavers = attendance_today.filter(left_early=True).count()

    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    in_progress_tasks = Task.objects.filter(status='in_progress').count()
    completed_tasks = Task.objects.filter(status='completed').count()

    context = {
       'today': today,
       'attendance_today': attendance_today,
       'total_staff': total_staff,
       'present_staff': present_staff,
       'absent_staff': absent_staff,
       'total_hours_worked': total_hours_worked,
       'late_staff': late_staff,
       'early_leavers': early_leavers,
       'total_tasks': total_tasks,
       'pending_tasks': pending_tasks,
       'in_progress_tasks': in_progress_tasks,
       'completed_tasks': completed_tasks,
    }

    return render(request, 'attendance/admin_dashboard.html', context)

@staff_required
def staff_check_in_out(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            staff = form.cleaned_data['staff']
            today = timezone.now().date()

            attendance, created = Attendance.objects.get_or_create(
                staff=staff,
                date=today
            )

            now = timezone.now().time()

            if not attendance.check_in:
                attendance.check_in = now
                attendance.save()
                messages.success(request, "Checked IN successfully!")
                return redirect('check_success')
            elif not attendance.check_out:
                attendance.check_out = now
                attendance.save()
                messages.success(request, "Checked OUT successfully!")
                return redirect('check_success')
            else:
                messages.warning(request, "⚠️ Already checked in and out today!")
                return render(request, 'attendance/check_in_out.html', {'form': form})
    else:
        form = AttendanceForm()

    return render(request, 'attendance/check_in_out.html', {'form': form})

@staff_required
def update_task_status(request, task_id, status):
    task = get_object_or_404(Task, id=task_id)
    valid_statuses = ['pending', 'in_progress', 'completed']
    if status not in valid_statuses:
        messages.error(request, "❌ Invalid status.")
        return redirect('task_list')

    task.status = status
    if status == 'completed':
        task.completed_at = timezone.now()
    else:
        task.completed_at = None
    task.save()
    messages.success(request, f"✅ Task '{task.title}' marked as {status.replace('_', ' ').title()}.")
    return redirect('task_list')

@staff_required
def staff_task_list(request):
    tasks = Task.objects.select_related('staff').order_by('-date_assigned')
    return render(request, 'attendance/task_list.html', {'tasks': tasks})