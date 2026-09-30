from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Task

User = get_user_model()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Full name")
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username or email")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get("identifier", "").strip()
        password = cleaned.get("password")
        if identifier and password:
            user = User.objects.filter(email__iexact=identifier).first()
            username = user.get_username() if user else identifier
            self.user = authenticate(self.request, username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Those login details didn't match an account.")
        return cleaned

    def get_user(self):
        return self.user


class TaskForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        label="Date and time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    reminder_at = forms.DateTimeField(
        label="Remind me at",
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Task
        fields = ("title", "description", "due_at", "reminder_at")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned = super().clean()
        due_at = cleaned.get("due_at")
        reminder_at = cleaned.get("reminder_at")
        if reminder_at and due_at and reminder_at > due_at:
            self.add_error("reminder_at", "Your reminder needs to be before the task is due.")
        if due_at and timezone.is_naive(due_at):
            cleaned["due_at"] = timezone.make_aware(due_at, timezone.get_current_timezone())
        if reminder_at and timezone.is_naive(reminder_at):
            cleaned["reminder_at"] = timezone.make_aware(reminder_at, timezone.get_current_timezone())
        return cleaned
