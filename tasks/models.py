from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_date = models.DateField()
    task_time = models.TimeField()
    reminder_time = models.TimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def _combine_datetime(self, date_value, time_value):
        dt = datetime.combine(date_value, time_value)
        if timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt

    @property
    def task_datetime(self):
        return self._combine_datetime(self.task_date, self.task_time)

    @property
    def reminder_datetime(self):
        return self._combine_datetime(self.task_date, self.reminder_time)

    @property
    def is_overdue(self):
        return not self.completed and self.task_datetime < timezone.now()

    @property
    def is_due_soon(self):
        if self.completed:
            return False
        now = timezone.now()
        return self.task_datetime > now and self.task_datetime <= now + timedelta(hours=1)

    @property
    def status_label(self):
        if self.completed:
            return 'Completed'
        if self.is_overdue:
            return 'Overdue'
        if self.is_due_soon:
            return 'Due Soon'
        return 'Upcoming'

    @property
    def status_class(self):
        status_map = {
            'Completed': 'completed',
            'Overdue': 'overdue',
            'Due Soon': 'due-soon',
            'Upcoming': 'upcoming',
        }
        return status_map.get(self.status_label, 'upcoming')
