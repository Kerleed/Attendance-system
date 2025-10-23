from django.db import models
from django.utils import timezone
import datetime
from datetime import timedelta


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.name}, {self.country.name}"
    

class LocalGovernment(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.name}, {self.state.name}"
    
class Staff(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, default="Unknown")

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    local_government = models.ForeignKey(LocalGovernment, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.other_names} {self.surname}".strip()

    def __str__(self):
        return self.full_name

class Attendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    is_late = models.BooleanField(default=False)
    left_early = models.BooleanField(default=False)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


    #location = models.CharField(max_length=255, blank=True) #optional location field

    def calculate_hours_worked(self):
        if self.check_in and self.check_out:
            in_time = datetime.combine(self.date, self.check_in)
            out_time = datetime.combine(self.date, self.check_out)
            duration = out_time - in_time
            return round(duration.total_seconds()/ 3600, 2)
        return 0
    
    def save(self, *args, **kwargs):
        if self.check_in and self.check_in > timezone.datetime.strptime("09:30", "%H:%M").time(): self.is_late = True
        else:
            self.is_late = False

        if self.check_out and self.check_out < timezone.datetime.strptime("17:00", "%H:%M").time():
            self.left_early = True
        else:
            self.left_early = False

        self.hours_worked = self.calculate_hours_worked()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.full_name} - {self.date}"

class Task(models.Model):
    STATUS_CHOICES = [
('pending', 'pending'),
('in_progress', 'In Progress'),
('completed', 'Completed'),
]
    
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_assigned = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.title} - {self.staff.first_name}"
    
    



        
        
    
    
