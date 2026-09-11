from __future__ import annotations

import uuid

import structlog

from src.infrastructure.queue.celery_app import app

logger = structlog.get_logger(__name__)

DEFAULT_LOOKAHEAD_DAYS = 14


@app.task(
    bind=True,
    name="src.infrastructure.queue.tasks.filing_deadline_scan.scan_filing_deadlines",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
)
def scan_filing_deadlines(self, lookahead_days: int = DEFAULT_LOOKAHEAD_DAYS) -> dict:
    """Find filings whose deadline falls within *lookahead_days*.

    Actions:
        - Flag as APPROACHING_DEADLINE / OVERDUE.
        - Enqueue notification for responsible entity admin.

    Returns:
        Summary dict.
    """
    request_id = str(uuid.uuid4())
    log = logger.bind(
        task="scan_filing_deadlines",
        lookahead_days=lookahead_days,
        request_id=request_id,
    )
    log.info("filing_deadline_scan_started")

    try:
        # --- stub ---
        flagged = 0
        overdue = 0

        log.info("filing_deadline_scan_completed", flagged=flagged, overdue=overdue)
        return {
            "status": "ok",
            "flagged": flagged,
            "overdue": overdue,
            "lookahead_days": lookahead_days,
        }

    except Exception as exc:
        log.error("filing_deadline_scan_failed", error=str(exc))
        raise self.retry(exc=exc)
