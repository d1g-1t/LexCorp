"""PoA expiry scanner (scheduled task).

Runs daily at 07:00 UTC via Celery Beat.
Finds powers-of-attorney expiring within the next N days and
dispatches notification tasks for each.
"""

from __future__ import annotations

import uuid

import structlog

from src.infrastructure.queue.celery_app import app

logger = structlog.get_logger(__name__)

DEFAULT_LOOKAHEAD_DAYS = 30


@app.task(
    bind=True,
    name="src.infrastructure.queue.tasks.poa_expiry_scan.scan_expiring_poa",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
)
def scan_expiring_poa(self, lookahead_days: int = DEFAULT_LOOKAHEAD_DAYS) -> dict:
    """Scan for PoA documents expiring within *lookahead_days*.

    For each hit:
        - Mark status → EXPIRING_SOON (if not already).
        - Enqueue notification for the responsible officer.

    Returns:
        Summary with counts of flagged / notified PoAs.
    """
    request_id = str(uuid.uuid4())
    log = logger.bind(
        task="scan_expiring_poa",
        lookahead_days=lookahead_days,
        request_id=request_id,
    )
    log.info("poa_expiry_scan_started")

    try:
        # --- stub ---
        # 1. SELECT * FROM powers_of_attorney
        #    WHERE status = 'active'
        #      AND expires_at <= now() + interval '{lookahead_days} days'
        # 2. For each row: update status, enqueue notification
        flagged = 0

        log.info("poa_expiry_scan_completed", flagged=flagged)
        return {
            "status": "ok",
            "flagged": flagged,
            "lookahead_days": lookahead_days,
        }

    except Exception as exc:
        log.error("poa_expiry_scan_failed", error=str(exc))
        raise self.retry(exc=exc)
