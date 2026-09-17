import django
from datetime import date, timedelta, time


django.setup()

from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()
user = User.objects.filter(username='demo_user').first() or User.objects.create_user(
    'demo_user',
    'demo@taskora.com',
    'demo1234',
)

Task.objects.filter(user=user).delete()

sample = [
    ('Deep work sprint', 'Complete the product strategy and focus block for the day.', date.today() + timedelta(days=0), time(18, 30), time(18, 15), False),
    ('Design review', 'Share the landing page mockups with the team and collect feedback.', date.today() + timedelta(days=1), time(10, 0), time(9, 40), False),
    ('Client follow-up', 'Send the updated proposal and confirm next meeting time.', date.today() + timedelta(days=2), time(15, 0), time(14, 45), False),
    ('Weekly planning', 'Review this week priorities and update project notes.', date.today() - timedelta(days=1), time(9, 0), time(8, 45), False),
    ('Finish portfolio', 'Polish the personal portfolio summary and upload final assets.', date.today() - timedelta(days=2), time(17, 0), time(16, 40), True),
]

for title, desc, task_date, task_time, reminder_time, completed in sample:
    Task.objects.create(
        user=user,
        title=title,
        description=desc,
        task_date=task_date,
        task_time=task_time,
        reminder_time=reminder_time,
        completed=completed,
    )

print(f'Created {len(sample)} demo tasks for {user.username}')
