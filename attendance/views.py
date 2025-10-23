from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm, AttendanceForm
from django.http import HttpResponse
from .models import Task, Attendance, Staff
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from accounts.utils import admin_required, staff_required

#today = timezone.localdate()

@login_required
@staff_required
def home(request):
    return render(request, 'home.html')

@staff_required
def dashboard(request):
    return render(request, 'dashboard.html')

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

            now = timezone.now()

            if not attendance.check_in:
                attendance.check_in = now
                attendance.save()
                #messages.success(request, "Checked IN successfully!")
                return redirect('check_success')
            
            elif not attendance.check_out:
                attendance.check_out= now
                attendance.save()
                #message.success(request, "Checked OUT successfully!")
                return redirect('check_success')
            

            else: 
                messages.warning(request, "⚠️ Already checked in and out today!")
                return render(request, 'check_in_out.html', {'form': form})
            

           # attendance.save()
            #return redirect('check_success')
    
    else:
        form = AttendanceForm()

    return render(request, 'check_in_out.html', {'form': form})

@staff_required
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

@staff_required
def staff_task_list(request):
    tasks = Task.objects.all().order_by('-date_assigned')
    return render(request, 'task_list.html', {'tasks': tasks})
