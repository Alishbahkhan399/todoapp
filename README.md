# Taskora

Taskora is a template-based Django task planner. It uses Django authentication, SQLite, Django templates, and vanilla JavaScript. No virtual environment or frontend framework is required.

## Requirements

- Python 3.10 or newer
- Django 5.2 or newer (Django 6.1 was used while building this project)

Install Django into the existing Python installation if it is not already available:

```powershell
python -m pip install "Django>=5.2,<7.0"
```

Do not create or activate a virtual environment for this project.

## Run the project

From the folder containing `manage.py`:

```powershell
python manage.py makemigrations tasks
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser. `createsuperuser` is optional unless you want to use the Django admin at `/admin/`.

To recreate the project structure from an empty folder with Django installed:

```powershell
python -m django startproject taskora .
python manage.py startapp tasks
```

The project and app are already scaffolded in this workspace. If PowerShell does not recognize `python`, use the Python launcher (`py`) in its place.

## Main files

- `manage.py` runs Django management commands.
- `taskora/settings.py` configures SQLite, installed apps, templates, static assets, and authentication redirects.
- `taskora/urls.py` routes admin and application URLs.
- `tasks/models.py` defines the user-owned task and its computed status.
- `tasks/forms.py` validates registration, login, task scheduling, and reminder timing.
- `tasks/views.py` implements authentication, profile, dashboard, and task workflows with user-scoped queries.
- `tasks/urls.py` maps application routes.
- `tasks/admin.py` configures task management in Django Admin.
- `tasks/migrations/` stores database schema migrations.
- `templates/tasks/` contains the page templates.
- `static/css/style.css` contains the responsive burgundy, black, and cream design.
- `static/js/main.js` contains navigation, password visibility, cursor, toast, and reminder behavior.
- `db.sqlite3` is created when migrations are applied.

## Reminders

Reminders are checked by JavaScript while the dashboard is open. The page checks every 15 seconds, shows an in-app dialog, and can use browser notifications after the user enables them. Browser notifications are not background push: reminders do not run when the site is closed. Tasks are stored in SQLite and visible only to their owner in the normal application.

## Deploy the frontend to Vercel

Import this GitHub repository into Vercel with the project root set to the repository root. `vercel.json` builds and deploys only the static landing page and its assets; Django authentication, task views, and SQLite are not deployed to Vercel. Set the Vercel environment variable `BACKEND_URL` to the public origin of the separately hosted Django app to enable the login and registration links. Without it, Vercel still serves the landing page, but account links remain unavailable.

## Checks

Run the workflow and ownership tests with:

```powershell
python manage.py test tasks
```
