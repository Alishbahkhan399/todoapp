from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
	title = models.CharField(max_length=180)
	description = models.TextField(blank=True)
	due_at = models.DateTimeField()
	reminder_at = models.DateTimeField(blank=True, null=True)
	completed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["completed", "due_at"]

	def __str__(self):
		return self.title

	@property
	def status(self):
		if self.completed:
			return "Completed"
		if self.due_at < timezone.now():
			return "Overdue"
		if self.due_at <= timezone.now() + timedelta(hours=2):
			return "Due soon"
		return "Upcoming"
