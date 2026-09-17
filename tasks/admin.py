from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'task_date', 'task_time', 'reminder_time', 'completed', 'created_at')
    list_filter = ('completed', 'task_date', 'user')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)
