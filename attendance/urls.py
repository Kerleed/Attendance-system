from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
    path('', views.home, name='attendance_home'),
    path('tasks/', views.staff_task_list, name='task_list'),
    path('check/', views.staff_check_in_out, name='staff_check'),
    path('check-success/', lambda request: HttpResponse("Check-in/out recorded!"), name='check_success'),
    path('update-task-status/<int:task_id>/<str:status>/', views.update_task_status, name='update_task_status'),
]