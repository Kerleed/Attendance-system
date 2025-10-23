from django import forms
from attendance.models import Task, Attendance

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['staff', 'title', 'description', 'date_assigned', 'status']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields =['staff']
