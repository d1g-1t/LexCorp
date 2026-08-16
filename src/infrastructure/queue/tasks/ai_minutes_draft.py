"""AI-powered meeting-minutes drafting task.

Runs on the lexcorp.ai queue.
Uses the Ollama-backed LLM (via LangChain) to:
  1. Summarise raw discussion notes.
  2. Extract action items with owners + deadlines.
  3. Produce a structured minutes document (Markdown → PDF).
"""

from __future__ import annotations

import uuid

import structlog

from src.infrastructure.queue.celery_app import app

logger = structlog.get_logger(__name__)


@app.task(
    bind=True,
    name="src.infrastructure.queue.tasks.ai_minutes_draft.draft_meeting_minutes",
    max_retries=2,
    default_retry_delay=90,
    acks_late=True,
)
def draft_meeting_minutes(self, meeting_id: str, raw_notes: str) -> dict:
    """Use LLM to draft polished meeting minutes from raw notes.

    Args:
        meeting_id: The UUID of the meeting.
        raw_notes: Free-form text captured during the meeting.

    Returns:
        Dict with Markdown minutes text and extracted action items.
    """
    request_id = str(uuid.uuid4())
    log = logger.bind(
        task="draft_meeting_minutes",
        meeting_id=meeting_id,
        request_id=request_id,
    )
    log.info("ai_minutes_draft_started")

    try:
        # --- stub: real impl uses LangChain + Ollama ---
        # from src.infrastructure.ai.llm_service import OllamaLLMService
        # llm = OllamaLLMService()
        # summary = await llm.summarise_meeting(raw_notes)
        # actions = await llm.extract_action_items(raw_notes)
        # minutes_md = await llm.draft_minutes(meeting_id, summary, actions)

        minutes_md = f"# Протокол заседания\n\n*Meeting {meeting_id}*\n\n> Черновик сформирован ИИ-ассистентом.\n\n{raw_notes}"
        actions: list[dict] = []

        log.info("ai_minutes_draft_completed", actions_count=len(actions))
        return {
            "status": "ok",
            "meeting_id": meeting_id,
            "minutes_markdown": minutes_md,
            "action_items": actions,
        }

    except Exception as exc:
        log.error("ai_minutes_draft_failed", error=str(exc))
        raise self.retry(exc=exc)
