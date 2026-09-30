from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm, TaskForm
from .models import Task


def home(request):
	if request.user.is_authenticated:
		return redirect("tasks:dashboard")
	return render(request, "tasks/home.html")


def register_view(request):
	if request.user.is_authenticated:
		return redirect("tasks:dashboard")
	form = RegisterForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.save()
		login(request, user)
		messages.success(request, "Your account is ready. Welcome to Taskora.")
		return redirect("tasks:dashboard")
	return render(request, "tasks/register.html", {"form": form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect("tasks:dashboard")
	form = LoginForm(request, request.POST or None)
	if request.method == "POST" and form.is_valid():
		login(request, form.get_user())
		messages.success(request, "Welcome back.")
		next_url = request.GET.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
			return redirect(next_url)
		return redirect("tasks:dashboard")
	return render(request, "tasks/login.html", {"form": form})


def logout_view(request):
	if request.method == "POST":
		logout(request)
		messages.success(request, "You have been logged out.")
	return redirect("tasks:home")


@login_required
def dashboard(request):
	user_tasks = Task.objects.filter(user=request.user)
	now = timezone.now()
	query = request.GET.get("q", "").strip()
	status_filter = request.GET.get("status", "all")
	sort = request.GET.get("sort", "due")
	tasks = user_tasks
	if query:
		tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
	if status_filter == "pending":
		tasks = tasks.filter(completed=False)
	elif status_filter == "completed":
		tasks = tasks.filter(completed=True)
	elif status_filter == "upcoming":
		tasks = tasks.filter(completed=False, due_at__gte=now)
	elif status_filter == "overdue":
		tasks = tasks.filter(completed=False, due_at__lt=now)
	ordering = {"newest": "-created_at", "oldest": "created_at", "latest": "-due_at"}.get(sort, "due_at")
	tasks = tasks.order_by(ordering)
	reminders = [
		{"id": item.id, "title": item.title, "reminder": item.reminder_at.isoformat(), "url": f"/tasks/{item.id}/"}
		for item in user_tasks.filter(completed=False, reminder_at__isnull=False)
	]
	context = {
		"tasks": tasks,
		"total_count": user_tasks.count(),
		"pending_count": user_tasks.filter(completed=False).count(),
		"completed_count": user_tasks.filter(completed=True).count(),
		"overdue_count": user_tasks.filter(completed=False, due_at__lt=now).count(),
		"query": query,
		"status_filter": status_filter,
		"sort": sort,
		"reminders": reminders,
		"greeting": "Good morning" if timezone.localtime().hour < 12 else "Good afternoon" if timezone.localtime().hour < 18 else "Good evening",
	}
	return render(request, "tasks/dashboard.html", context)


@login_required
def task_create(request):
	form = TaskForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		task = form.save(commit=False)
		task.user = request.user
		task.save()
		messages.success(request, "Task created successfully.")
		return redirect("tasks:dashboard")
	return render(request, "tasks/task_form.html", {"form": form, "is_edit": False})


@login_required
def task_detail(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_edit(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	form = TaskForm(request.POST or None, instance=task)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Task updated successfully.")
		return redirect("tasks:task_detail", pk=task.pk)
	return render(request, "tasks/task_form.html", {"form": form, "is_edit": True, "task": task})


@login_required
def task_toggle(request, pk):
	if request.method == "POST":
		task = get_object_or_404(Task, pk=pk, user=request.user)
		task.completed = not task.completed
		task.save(update_fields=["completed", "updated_at"])
		messages.success(request, "Task completed." if task.completed else "Task moved back to pending.")
	next_url = request.POST.get("next", "")
	if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
		return redirect(next_url)
	return redirect("tasks:dashboard")


@login_required
def task_delete(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	if request.method == "POST":
		task.delete()
		messages.success(request, "Task deleted successfully.")
		return redirect("tasks:dashboard")
	return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
def profile(request):
	user_tasks = Task.objects.filter(user=request.user)
	return render(request, "tasks/profile.html", {
		"total_count": user_tasks.count(),
		"completed_count": user_tasks.filter(completed=True).count(),
		"pending_count": user_tasks.filter(completed=False).count(),
	})


@login_required
def password_change_done(request):
	return render(request, "tasks/password_change_done.html")
