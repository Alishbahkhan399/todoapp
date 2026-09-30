from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Task

User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TaskWorkflowTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username="owner", password="A-long-safe-passphrase-384!")
		self.other_user = User.objects.create_user(username="other", password="A-long-safe-passphrase-384!")
		self.task = Task.objects.create(
			user=self.owner,
			title="Plan the week",
			due_at=timezone.now() + timedelta(hours=4),
			reminder_at=timezone.now() + timedelta(hours=3),
		)

	def test_dashboard_requires_authentication(self):
		response = self.client.get(reverse("tasks:dashboard"))
		self.assertRedirects(response, f"{reverse('tasks:login')}?next={reverse('tasks:dashboard')}")

	def test_users_cannot_view_or_change_another_users_task(self):
		self.client.force_login(self.other_user)
		detail = self.client.get(reverse("tasks:task_detail", args=[self.task.pk]))
		toggle = self.client.post(reverse("tasks:task_toggle", args=[self.task.pk]))
		self.assertEqual(detail.status_code, 404)
		self.assertEqual(toggle.status_code, 404)
		self.task.refresh_from_db()
		self.assertFalse(self.task.completed)

	def test_registration_and_email_login(self):
		response = self.client.post(reverse("tasks:register"), {
			"first_name": "New User",
			"username": "new-user",
			"email": "new@example.com",
			"password1": "A-long-safe-passphrase-384!",
			"password2": "A-long-safe-passphrase-384!",
		})
		self.assertRedirects(response, reverse("tasks:dashboard"))
		self.client.post(reverse("tasks:logout"))
		response = self.client.post(reverse("tasks:login"), {
			"identifier": "new@example.com",
			"password": "A-long-safe-passphrase-384!",
		})
		self.assertRedirects(response, reverse("tasks:dashboard"))

	def test_login_rejects_external_next_url(self):
		response = self.client.post(f"{reverse('tasks:login')}?next=https://example.com", {
			"identifier": "owner",
			"password": "A-long-safe-passphrase-384!",
		})
		self.assertRedirects(response, reverse("tasks:dashboard"))

	def test_task_create_complete_restore_edit_and_delete(self):
		self.client.force_login(self.owner)
		due_at = (timezone.localtime(timezone.now()) + timedelta(days=1)).replace(second=0, microsecond=0)
		reminder_at = due_at - timedelta(minutes=15)
		response = self.client.post(reverse("tasks:task_create"), {
			"title": "Submit the proposal",
			"description": "Final review",
			"due_at": due_at.strftime("%Y-%m-%dT%H:%M"),
			"reminder_at": reminder_at.strftime("%Y-%m-%dT%H:%M"),
		})
		self.assertRedirects(response, reverse("tasks:dashboard"))
		task = Task.objects.get(title="Submit the proposal", user=self.owner)
		self.client.post(reverse("tasks:task_toggle", args=[task.pk]))
		task.refresh_from_db()
		self.assertTrue(task.completed)
		self.client.post(reverse("tasks:task_toggle", args=[task.pk]))
		task.refresh_from_db()
		self.assertFalse(task.completed)
		response = self.client.post(reverse("tasks:task_edit", args=[task.pk]), {
			"title": "Send the proposal",
			"description": "Final review",
			"due_at": due_at.strftime("%Y-%m-%dT%H:%M"),
			"reminder_at": reminder_at.strftime("%Y-%m-%dT%H:%M"),
		})
		self.assertRedirects(response, reverse("tasks:task_detail", args=[task.pk]))
		task.refresh_from_db()
		self.assertEqual(task.title, "Send the proposal")
		self.client.post(reverse("tasks:task_delete", args=[task.pk]))
		self.assertFalse(Task.objects.filter(pk=task.pk).exists())

	def test_dashboard_search_and_overdue_filter_are_user_scoped(self):
		Task.objects.create(user=self.owner, title="Late report", due_at=timezone.now() - timedelta(hours=1))
		Task.objects.create(user=self.other_user, title="Private report", due_at=timezone.now() - timedelta(hours=1))
		self.client.force_login(self.owner)
		response = self.client.get(reverse("tasks:dashboard"), {"q": "report", "status": "overdue"})
		self.assertContains(response, "Late report")
		self.assertNotContains(response, "Private report")

	def test_reminder_after_due_time_is_rejected(self):
		self.client.force_login(self.owner)
		due_at = (timezone.localtime(timezone.now()) + timedelta(hours=2)).replace(second=0, microsecond=0)
		response = self.client.post(reverse("tasks:task_create"), {
			"title": "Invalid reminder",
			"due_at": due_at.strftime("%Y-%m-%dT%H:%M"),
			"reminder_at": (due_at + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M"),
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Your reminder needs to be before the task is due.")
