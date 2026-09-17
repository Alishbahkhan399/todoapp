import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import RegistrationForm, TaskForm
from .models import Task


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tasks/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome to Taskora!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'tasks/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home')


@login_required
def dashboard(request):
    tasks = list(Task.objects.filter(user=request.user))
    search_query = (request.GET.get('search') or '').strip()
    status_filter = request.GET.get('status', 'all')
    sort_option = request.GET.get('sort', 'newest')

    if search_query:
        query = search_query.lower()
        tasks = [
            task for task in tasks
            if query in task.title.lower() or query in (task.description or '').lower()
        ]

    if status_filter == 'pending':
        tasks = [task for task in tasks if not task.completed]
    elif status_filter == 'completed':
        tasks = [task for task in tasks if task.completed]
    elif status_filter == 'upcoming':
        tasks = [task for task in tasks if not task.completed and not task.is_overdue and task.task_datetime > timezone.now()]
    elif status_filter == 'overdue':
        tasks = [task for task in tasks if task.is_overdue]

    if sort_option == 'oldest':
        tasks.sort(key=lambda task: (task.task_date, task.task_time, task.created_at))
    elif sort_option == 'due_soonest':
        tasks.sort(key=lambda task: task.task_datetime)
    elif sort_option == 'due_latest':
        tasks.sort(key=lambda task: task.task_datetime, reverse=True)
    else:
        tasks.sort(key=lambda task: task.created_at, reverse=True)

    total_tasks = Task.objects.filter(user=request.user).count()
    pending_tasks = Task.objects.filter(user=request.user, completed=False).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    overdue_tasks = sum(1 for task in Task.objects.filter(user=request.user, completed=False) if task.is_overdue)

    tasks_json = [
        {
            'id': task.id,
            'title': task.title,
            'reminder_datetime': task.reminder_datetime.isoformat(),
            'task_datetime': task.task_datetime.isoformat(),
            'url': reverse('task_detail', args=[task.id]),
            'completed': task.completed,
        }
        for task in Task.objects.filter(user=request.user, completed=False)
    ]

    context = {
        'tasks': tasks,
        'tasks_json': json.dumps(tasks_json),
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_option': sort_option,
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form, 'editing': False})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'editing': True, 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save(update_fields=['completed', 'updated_at'])
        if task.completed:
            messages.success(request, 'Task completed successfully.')
        else:
            messages.success(request, 'Task restored to pending.')
    return redirect('dashboard')


@login_required
def profile(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = tasks.filter(completed=False).count()

    context = {
        'user': request.user,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'tasks/profile.html', context)
