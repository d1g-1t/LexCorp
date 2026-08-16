"""Meeting reminder task.

Sends reminders to board members N days before a scheduled meeting.
Channels: email, Slack, in-app notification.
"""

from __future__ import annotations

import uuid

import structlog

from src.infrastructure.queue.celery_app import app

logger = structlog.get_logger(__name__)


@app.task(
    bind=True,
    name="src.infrastructure.queue.tasks.meeting_reminder.send_meeting_reminder",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def send_meeting_reminder(self, meeting_id: str, days_before: int = 3) -> dict:
    """Send meeting reminders to all invited participants.

    Args:
        meeting_id: UUID of the scheduled meeting.
        days_before: How many days in advance this reminder fires.

    Returns:
        Summary dict with delivery count.
    """
    request_id = str(uuid.uuid4())
    log = logger.bind(
        task="send_meeting_reminder",
        meeting_id=meeting_id,
        days_before=days_before,
        request_id=request_id,
    )
    log.info("meeting_reminder_started")

    try:
        # --- stub ---
        # 1. Fetch meeting + participants
        # 2. Build notification payload (subject, body, ICS attachment)
        # 3. Dispatch via email / Slack / in-app
        delivered = 0  # placeholder

        log.info("meeting_reminder_completed", delivered=delivered)
        return {
            "status": "ok",
            "meeting_id": meeting_id,
            "delivered": delivered,
        }

    except Exception as exc:
        log.error("meeting_reminder_failed", error=str(exc))
        raise self.retry(exc=exc)
