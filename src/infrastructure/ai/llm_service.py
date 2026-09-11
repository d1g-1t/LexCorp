from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.application.interfaces import ILLMAssistant
from src.infrastructure.ai.prompts import (
    COMPLIANCE_CHECK_PROMPT,
    DRAFT_MINUTES_PROMPT,
    EXTRACT_ACTION_ITEMS_PROMPT,
    RISK_ASSESSMENT_PROMPT,
    SUMMARISE_MEETING_PROMPT,
    SYSTEM_PROMPT,
)
from src.infrastructure.observability.metrics import ai_duration_histogram, ai_failures, ai_runs

logger = structlog.get_logger(__name__)


class OllamaLLMService(ILLMAssistant):
    """Concrete LLM assistant backed by a self-hosted Ollama instance."""

    def __init__(
        self,
        base_url: str = "http://localhost:9434",
        model: str = "llama3",
        temperature: float = 0.1,
        request_timeout: float = 120.0,
    ) -> None:
        self._llm = Ollama(
            base_url=base_url,
            model=model,
            temperature=temperature,
            timeout=request_timeout,
        )
        self._parser = StrOutputParser()
        self._model_name = model
        logger.info("ollama_llm_service_init", base_url=base_url, model=model)

    # ------------------------------------------------------------------
    #  ILLMAssistant interface
    # ------------------------------------------------------------------

    async def summarise_meeting(self, raw_notes: str) -> str:
        """Produce a concise summary of meeting notes."""
        return await self._invoke(
            "summarise_meeting",
            SUMMARISE_MEETING_PROMPT,
            system=SYSTEM_PROMPT,
            raw_notes=raw_notes,
        )

    async def extract_action_items(self, minutes_text: str) -> list[dict[str, Any]]:
        """Extract structured action items from minutes text."""
        raw = await self._invoke(
            "extract_action_items",
            EXTRACT_ACTION_ITEMS_PROMPT,
            system=SYSTEM_PROMPT,
            minutes_text=minutes_text,
        )
        return self._safe_json_parse(raw, fallback=[])

    async def draft_minutes(
        self,
        meeting_id: str,
        meeting_date: str,
        participants: str,
        agenda: str,
        summary: str,
        action_items_json: str,
    ) -> str:
        """Draft full meeting minutes in Markdown."""
        return await self._invoke(
            "draft_minutes",
            DRAFT_MINUTES_PROMPT,
            system=SYSTEM_PROMPT,
            meeting_id=meeting_id,
            meeting_date=meeting_date,
            participants=participants,
            agenda=agenda,
            summary=summary,
            action_items_json=action_items_json,
        )

    async def assess_governance_risk(self, governance_data: str) -> dict[str, Any]:
        """Run AI-powered governance risk assessment."""
        raw = await self._invoke(
            "risk_assessment",
            RISK_ASSESSMENT_PROMPT,
            system=SYSTEM_PROMPT,
            governance_data=governance_data,
        )
        return self._safe_json_parse(raw, fallback={"overall_risk": "unknown", "risk_factors": []})

    async def check_compliance(
        self,
        document_type: str,
        document_content: str,
        applicable_regulations: str,
    ) -> dict[str, Any]:
        """Check a document against applicable regulations."""
        raw = await self._invoke(
            "compliance_check",
            COMPLIANCE_CHECK_PROMPT,
            system=SYSTEM_PROMPT,
            document_type=document_type,
            document_content=document_content,
            applicable_regulations=applicable_regulations,
        )
        return self._safe_json_parse(raw, fallback={"compliant": False, "issues": []})

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    async def _invoke(self, task_name: str, prompt_template: str, **kwargs: str) -> str:
        """Common invoke wrapper with metrics & error handling."""
        ai_runs.labels(task=task_name, model=self._model_name).inc()
        log = logger.bind(task=task_name, model=self._model_name)
        log.info("llm_invoke_started")

        try:
            prompt = ChatPromptTemplate.from_template(prompt_template)
            chain = prompt | self._llm | self._parser

            with ai_duration_histogram.labels(task=task_name).time():
                result: str = await chain.ainvoke(kwargs)

            log.info("llm_invoke_completed", response_length=len(result))
            return result.strip()

        except Exception as exc:
            ai_failures.labels(task=task_name, model=self._model_name).inc()
            log.error("llm_invoke_failed", error=str(exc))
            raise

    @staticmethod
    def _safe_json_parse(raw: str, fallback: Any) -> Any:
        """Try to parse JSON from LLM output; return *fallback* on failure."""
        try:
            # LLM may wrap JSON in ```json ... ```
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError):
            logger.warning("llm_json_parse_failed", raw_snippet=raw[:200])
            return fallback
