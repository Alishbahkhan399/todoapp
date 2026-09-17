from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Task


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'Your full name'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_date', 'task_time', 'reminder_time']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Complete Django project'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Finish the authentication and dashboard implementation.'}),
            'task_date': forms.DateInput(attrs={'type': 'date'}),
            'task_time': forms.TimeInput(attrs={'type': 'time'}),
            'reminder_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        task_date = cleaned_data.get('task_date')
        task_time = cleaned_data.get('task_time')
        reminder_time = cleaned_data.get('reminder_time')

        if task_date and task_time and reminder_time:
            task_dt = datetime.combine(task_date, task_time)
            reminder_dt = datetime.combine(task_date, reminder_time)
            if reminder_dt > task_dt:
                raise forms.ValidationError('Reminder time must be earlier than or equal to the task time.')

        return cleaned_data
