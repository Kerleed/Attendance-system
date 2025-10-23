from django.contrib import admin
from .models import Task, Staff, Attendance, Country, State, LocalGovernment

admin.site.register(Task)
admin.site.register(Staff)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(LocalGovernment)
admin.site.register(Attendance)

