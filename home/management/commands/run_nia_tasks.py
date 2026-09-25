from django.core.management.base import BaseCommand

from home.models import NiaAuditLog, NiaTask
from home.nia_phone import place_nia_call_for_user


class Command(BaseCommand):
    help = "Run due, enabled Nia proactive call tasks once."

    def handle(self, *args, **options):
        from django.utils import timezone

        now = timezone.now()
        tasks = list(
            NiaTask.objects.select_related("user")
            .filter(enabled=True, next_run_at__isnull=False, next_run_at__lte=now)
            .order_by("next_run_at", "id")[:25]
        )

        if not tasks:
            self.stdout.write("No due Nia tasks.")
            return

        for task in tasks:
            try:
                session = place_nia_call_for_user(task.user, task_instruction=task.instruction)
                task.last_run_at = now
                task.last_result = f"Call queued: {session.id}"
                # Tasks are one-shot until a recurrence model is added.
                task.enabled = False
                task.next_run_at = None
                task.save(update_fields=["last_run_at", "last_result", "enabled", "next_run_at", "updated_at"])
                NiaAuditLog.objects.create(user=task.user, role=task.role, action="proactive_task_call_queued", detail={"task_id": task.id, "session_id": str(session.id)})
                self.stdout.write(self.style.SUCCESS(f"Nia task {task.id}: call queued."))
            except Exception as exc:
                task.last_run_at = now
                task.last_result = f"Call not placed: {exc}"[:500]
                task.next_run_at = now + timezone.timedelta(minutes=15)
                task.save(update_fields=["last_run_at", "last_result", "next_run_at", "updated_at"])
                NiaAuditLog.objects.create(user=task.user, role=task.role, action="proactive_task_call_failed", detail={"task_id": task.id, "error": str(exc)[:300]})
                self.stdout.write(self.style.WARNING(f"Nia task {task.id}: {exc}"))
