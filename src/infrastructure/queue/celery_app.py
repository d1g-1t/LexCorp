from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

redis_url = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:9379/1",
)

app = Celery(
    "lexcorp",
    broker=redis_url,
    backend=redis_url,
    include=[
        "src.infrastructure.queue.tasks.board_pack_generation",
        "src.infrastructure.queue.tasks.meeting_reminder",
        "src.infrastructure.queue.tasks.poa_expiry_scan",
        "src.infrastructure.queue.tasks.filing_deadline_scan",
        "src.infrastructure.queue.tasks.governance_analytics_refresh",
        "src.infrastructure.queue.tasks.ai_minutes_draft",
    ],
)

# ---------- serialisation ----------
app.conf.accept_content = ["json"]
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# ---------- routing ----------
app.conf.task_routes = {
    "src.infrastructure.queue.tasks.board_pack_generation.*": {"queue": "lexcorp.meetings"},
    "src.infrastructure.queue.tasks.meeting_reminder.*": {"queue": "lexcorp.meetings"},
    "src.infrastructure.queue.tasks.poa_expiry_scan.*": {"queue": "lexcorp.calendar"},
    "src.infrastructure.queue.tasks.filing_deadline_scan.*": {"queue": "lexcorp.calendar"},
    "src.infrastructure.queue.tasks.governance_analytics_refresh.*": {"queue": "lexcorp.analytics"},
    "src.infrastructure.queue.tasks.ai_minutes_draft.*": {"queue": "lexcorp.ai"},
}

# ---------- beat schedule ----------
app.conf.beat_schedule = {
    "scan-expiring-poa-every-morning": {
        "task": "src.infrastructure.queue.tasks.poa_expiry_scan.scan_expiring_poa",
        "schedule": crontab(hour=7, minute=0),
        "options": {"queue": "lexcorp.calendar"},
    },
    "scan-filing-deadlines-daily": {
        "task": "src.infrastructure.queue.tasks.filing_deadline_scan.scan_filing_deadlines",
        "schedule": crontab(hour=7, minute=30),
        "options": {"queue": "lexcorp.calendar"},
    },
    "refresh-governance-analytics-hourly": {
        "task": "src.infrastructure.queue.tasks.governance_analytics_refresh.refresh_analytics",
        "schedule": crontab(minute=0),  # every hour
        "options": {"queue": "lexcorp.analytics"},
    },
}

# ---------- reliability ----------
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.task_reject_on_worker_lost = True
app.conf.task_track_started = True

# ---------- result ----------
app.conf.result_expires = 3600  # 1h

if __name__ == "__main__":
    app.start()
