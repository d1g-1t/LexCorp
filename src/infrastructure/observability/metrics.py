"""Prometheus metrics for governance operations."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# ── Entity metrics ──────────────────────────────────
lexcorp_entities_total = Counter(
    "lexcorp_entities_total",
    "Total number of legal entities ever created",
    ["tenant_id"],
)
lexcorp_active_entities_total = Gauge(
    "lexcorp_active_entities_total",
    "Current active legal entities",
    ["tenant_id"],
)

# ── Meeting metrics ─────────────────────────────────
lexcorp_meetings_total = Counter(
    "lexcorp_meetings_total",
    "Total board meetings created",
    ["entity_id", "meeting_type"],
)
lexcorp_meetings_upcoming_total = Gauge(
    "lexcorp_meetings_upcoming_total",
    "Upcoming meetings count",
)

# ── Compliance / filing metrics ─────────────────────
lexcorp_obligations_overdue_total = Gauge(
    "lexcorp_obligations_overdue_total",
    "Current overdue compliance obligations",
)
lexcorp_poa_expiring_total = Gauge(
    "lexcorp_poa_expiring_total",
    "PoAs expiring within warning window",
)
lexcorp_filing_deadlines_due_total = Gauge(
    "lexcorp_filing_deadlines_due_total",
    "Filing deadlines due within warning window",
)

# ── AI metrics ──────────────────────────────────────
lexcorp_ai_runs_total = Counter(
    "lexcorp_ai_runs_total",
    "Total AI analysis pipeline runs",
    ["pipeline_type"],
)
lexcorp_ai_failures_total = Counter(
    "lexcorp_ai_failures_total",
    "Failed AI pipeline runs",
    ["pipeline_type"],
)

# ── Duration histograms ─────────────────────────────
lexcorp_board_pack_generation_duration_seconds = Histogram(
    "lexcorp_board_pack_generation_duration_seconds",
    "Time to generate board pack",
    buckets=[0.5, 1, 2, 5, 10, 30, 60],
)
lexcorp_minutes_draft_duration_seconds = Histogram(
    "lexcorp_minutes_draft_duration_seconds",
    "Time to draft meeting minutes via AI",
    buckets=[1, 2, 5, 10, 30, 60, 120],
)
lexcorp_calendar_scan_duration_seconds = Histogram(
    "lexcorp_calendar_scan_duration_seconds",
    "Time to scan calendar for deadlines",
    buckets=[0.1, 0.5, 1, 2, 5],
)
