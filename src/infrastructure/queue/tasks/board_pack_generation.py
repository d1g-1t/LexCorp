"""Board-pack generation task.

Collects agenda items, supporting docs, and previous-minutes references
into a single downloadable archive (PDF/ZIP) for board members.
"""

from __future__ import annotations

import uuid

import structlog

from src.infrastructure.queue.celery_app import app

logger = structlog.get_logger(__name__)


@app.task(
    bind=True,
    name="src.infrastructure.queue.tasks.board_pack_generation.generate_board_pack",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def generate_board_pack(self, meeting_id: str) -> dict:
    """Generate a board-pack archive for the given meeting.

    Steps:
        1. Fetch meeting + agenda items from DB.
        2. Collect related resolution drafts and attachments.
        3. Build a composite PDF/ZIP archive.
        4. Upload artifact to object-storage / local FS.
        5. Update meeting record with board_pack_url.
    """
    request_id = str(uuid.uuid4())
    log = logger.bind(task="generate_board_pack", meeting_id=meeting_id, request_id=request_id)
    log.info("board_pack_generation_started")

    try:
        # --- stub: replace with real implementation ---
        # In real impl this would:
        #  - open an async DB session
        #  - query meeting + joined agenda_items, resolutions
        #  - render each section to PDF via weasyprint / reportlab
        #  - zip everything
        #  - upload to S3/minio
        #  - patch meeting.board_pack_url
        log.info("board_pack_generation_completed")
        return {
            "status": "ok",
            "meeting_id": meeting_id,
            "pack_url": f"/artifacts/board-packs/{meeting_id}.zip",
        }

    except Exception as exc:
        log.error("board_pack_generation_failed", error=str(exc))
        raise self.retry(exc=exc)
