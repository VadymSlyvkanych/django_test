import os
import sys
from datetime import timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from test_app.models import Task, SubTask


def main():
    today = timezone.now()
    print(f"Today: {today.date()}\n")

    # ===================== CREATE =====================
    print("=" * 60)
    print("CREATE")
    print("=" * 60)

    task = Task.objects.create(
        title="Prepare presentation",
        description="Prepare materials and slides for the presentation",
        status="new",
        deadline=today + timedelta(days=3),
    )
    print(f"Created Task: '{task.title}' | status: {task.status} | deadline: {task.deadline.date()}")

    subtask1 = SubTask.objects.create(
        task=task,
        title="Gather information",
        description="Find necessary information for the presentation",
        status="new",
        deadline=today + timedelta(days=2),
    )
    print(f"Created SubTask: '{subtask1.title}' | status: {subtask1.status} | deadline: {subtask1.deadline.date()}")

    subtask2 = SubTask.objects.create(
        task=task,
        title="Create slides",
        description="Create presentation slides",
        status="new",
        deadline=today + timedelta(days=1),
    )
    print(f"Created SubTask: '{subtask2.title}' | status: {subtask2.status} | deadline: {subtask2.deadline.date()}\n")

    # ===================== READ =====================
    print("=" * 60)
    print("READ")
    print("=" * 60)

    # Tasks with status "New"
    new_tasks = Task.objects.filter(status="new")
    print(f"\nTasks with status 'new' ({new_tasks.count()}):")
    for t in new_tasks:
        print(f"  - ID {t.id}: '{t.title}' | status: {t.status} | deadline: {t.deadline.date()}")

    # Subtasks with status "Done" and overdue
    overdue_done_subtasks = SubTask.objects.filter(status="done", deadline__lt=timezone.now())
    print(f"\nSubtasks with status 'done' and past deadline ({overdue_done_subtasks.count()}):")
    for s in overdue_done_subtasks:
        print(f"  - ID {s.id}: '{s.title}' | status: {s.status} | deadline: {s.deadline.date()}")
    print()

    # ===================== UPDATE =====================
    print("=" * 60)
    print("UPDATE")
    print("=" * 60)

    # Change status of "Prepare presentation" to "In progress"
    task.status = "in_progress"
    task.save()
    print(f"\nUpdated Task '{task.title}' status → {task.status}")

    # Change deadline of "Gather information" to 2 days ago
    subtask1.refresh_from_db()
    subtask1.deadline = timezone.now() - timedelta(days=2)
    subtask1.save()
    print(f"Updated SubTask '{subtask1.title}' deadline → {subtask1.deadline.date()}")

    # Change description of "Create slides"
    subtask2.refresh_from_db()
    subtask2.description = "Create and format presentation slides"
    subtask2.save()
    print(f"Updated SubTask '{subtask2.title}' description → '{subtask2.description}'\n")

    # ===================== DELETE =====================
    print("=" * 60)
    print("DELETE")
    print("=" * 60)

    subtask_count_before = SubTask.objects.filter(task=task).count()
    task_title = task.title
    task.delete()  # CASCADE deletes all subtasks
    print(f"\nDeleted Task '{task_title}' (and {subtask_count_before} subtask(s) via CASCADE)")

    # Verify deletion
    task_exists = Task.objects.filter(title="Prepare presentation").exists()
    subtask_exists = SubTask.objects.filter(title="Gather information").exists()
    print(f"Task still exists: {task_exists}")
    print(f"SubTask still exists: {subtask_exists}")


if __name__ == "__main__":
    main()

# uv run queries.py
