from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('dashboard', views.admin_dashboard, name='admin_dashboard_root'),
    path('assign-task/', views.assign_task, name='assign_task'),
    path('tasks/', views.task_list, name='task_list'),
    path('task-success/', views.task_success, name='task_success'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('daily-overview/', views.daily_overview, name='daily_overview'),
    path('summary/', views.staff_perfomance_summary, name='staff_perfomance_summary'),
    path('update-task-status/<int:task_id>/<str:status>/', views.update_task_status, name='update_task_status'),
    path('assign-role/', views.assign_user_role, name='assign_user_role')
]