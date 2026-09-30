from django.contrib.auth.views import PasswordChangeView
from django.urls import path, reverse_lazy

from . import views

app_name = "tasks"
urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/toggle/", views.task_toggle, name="task_toggle"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("profile/", views.profile, name="profile"),
    path("profile/password/", PasswordChangeView.as_view(
        template_name="tasks/password_change.html",
        success_url=reverse_lazy("tasks:password_change_done"),
    ), name="password_change"),
    path("profile/password/done/", views.password_change_done, name="password_change_done"),
]
