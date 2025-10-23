from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm, AttendanceForm
from django.http import HttpResponse
from attendance.models import Task, Attendance, Staff
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from accounts.decorators import admin_required, staff_required
from accounts.utils import is_admin


#today = timezone.localdate()

def home(request):
    return render(request, 'home.html')

@login_required
@admin_required
def admin_dashboard(request):
    today = timezone.now().date()

    attendance_today = Attendance.objects.filter(date=today)
    total_staff = Staff.objects.count()
    present_staff = attendance_today.count()
    absent_staff = total_staff - present_staff

    total_hours_worked = attendance_today.aggregate(Sum('hours_worked'))
    ['hours_worked_sum'] or 0

    late_staff = attendance_today.filter(is_late=True).count()
    early_leavers = attendance_today.filter(left_early=True).count()

    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    in_progress_tasks = Task.objects.filter(status='in_progress').count()
    completed_tasks = Task.objects.filter(status='completed_tasks').count()


    context = {
       'today': today,
        'attendance_today': attendance_today,
        'total_staff': total_staff,
        'present_staff': present_staff,
        'absent_staff': absent_staff,
        'total_hours_worked': total_hours_worked,
        'late_staff': late_staff,
        'early_leavers': early_leavers,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
    }

    return render(request, 'attendance/admin_dashboard.html', context)

@admin_required
def staff_perfomance_summary(request):
    staff_summary = (
        Attendance.objects
        .values('staff__first_name', 'staff__surname')
        .annotate(
            total_hours=Sum('hours_worked'),
            total_days=Count('id')
        )
            .order_by('-total_hours')
    )
    context = {'staff_summary': staff_summary}
    return render(request, 'attendance/staff_summary.html', context)

@admin_required
def daily_overview(request):
    today = date.today()
    staff_list = Staff.objects.all()

    #Prefetch attendance data to avoid N+1 queries
    attendance_records = Attendance.objects.filter(date=today).select_related('staff')
    attendance_map = {att.staff_id: att for att in attendance_records}

    overview = []
    for staff in staff_list:
        """attendance = attendance.objects.filter(staff=staff, date=today).first()
        If there are 100 staffs that brings out 100 queries which will be slow n + 0 (perfomance issue)"""
        
        attendance = attendance_map.get(staff.id)

        if attendance:
            status = "Present"
            check_in = attendance.check_in
            check_out = attendance.check_out
            hours = attendance.hours_worked
            late = attendance.is_late
            early = attendance.left_early

        else:
            status = "Absent"
            check_in = check_out = hours = late = early = None

        overview.append({
            'staff': staff,
            'status': status,
            'check_in': check_in,
            'check_out': check_out,
            'hours': hours,
            'late': late,
            'early': early,
            })

        context = {'overview': overview, 'today': today}
        return render(request, 'attendance/daily_overview.html', context)

@admin_required
def update_task_status(request, task_id, status):
        task = get_object_or_404(Task, id=task_id)
       
        valid_statuses = ['pending', 'in_progress', 'completetd']
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

@admin_required
def attendance_summary(request):
    today = date.today()
    start_date = today - timedelta(days=30)

    staff_list = Staff.objects.all()

    summary = []

    for staff in staff_list:
        records = Attendance.objects.filter(staff=staff, date__range=[start_date, today])
        present_days = records.count()
        total_days = sum(1 for i in range(31) if (start_date + timedelta(days=i)).weekday() <5)
        absent_days = total_days - present_days
        total_hours = records.aggregate(total=Sum('hours_worked'))['total'] or 0

    
        avg_hours = round(total_hours / present_days, 2) if present_days > 0 else 0

        summary.append({
            'staff': staff,
            'present_days': present_days,
            'absent_days': absent_days,
            'total_hours': total_hours,
            'avg_hours': avg_hours,
        })

    context = {
        'summary': summary,
        'start_date': start_date,
        'end_date': today,
    }

    return render(request, 'attendance/attendance_summary.html', context)
            
@admin_required
def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_success') 
    else:
        form = TaskForm()

    return render(request, 'assign_task.html', {'form': form})

def task_success(request):
    return HttpResponse("🎉 Task was successfully assigned!")

@admin_required
def task_list(request):
    tasks = Task.objects.all().order_by('-date_assigned')
    return render(request, 'task_list.html', {'tasks': tasks})

@admin_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'edit_task.html', {'form': form, 'task': task})

@admin_required
def assign_user_role(request):
    """
    Allow an admin to assign a role (group) to a user.
    Backend logic only — no fancy frontend yet.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        group_name = request.POST.get("group_name")

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=group_name)

            # Remove old roles first
            user.groups.clear()
            # Assign new role
            user.groups.add(group)

            messages.success(request, f"✅ {user.username} is now a {group_name}!")
            return redirect("assign_user_role")

        except User.DoesNotExist:
            messages.error(request, "❌ User not found.")
        except Group.DoesNotExist:
            messages.error(request, "❌ Group not found.")

    users = User.objects.all()
    groups = Group.objects.all()

    context = {
        "users": users,
        "groups": groups,
    }

    return render(request, "attendance/assign_user_role.html", context)
