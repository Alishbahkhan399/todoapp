from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("title", "user", "due_at", "reminder_at", "completed", "created_at")
	list_filter = ("completed", "due_at", "created_at")
	search_fields = ("title", "description", "user__username", "user__email")
	readonly_fields = ("created_at", "updated_at")
