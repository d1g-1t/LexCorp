"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-31
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tenants ──────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(128), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── api_users ────────────────────────────────────
    op.create_table(
        "api_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── legal_entities ───────────────────────────────
    op.create_table(
        "legal_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("short_name", sa.String(255), nullable=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("ogrn", sa.String(15), nullable=True),
        sa.Column("jurisdiction", sa.String(128), nullable=False),
        sa.Column("registration_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("parent_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id"), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_entities_status", "legal_entities", ["tenant_id", "status"])

    # ── corporate_officers ───────────────────────────
    op.create_table(
        "corporate_officers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("position_title", sa.String(255), nullable=False),
        sa.Column("appointed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ceased_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("authority_scope", postgresql.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    # ── ownership_links ──────────────────────────────
    op.create_table(
        "ownership_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parent_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("child_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ownership_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("voting_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
    )

    # ── board_meetings ───────────────────────────────
    op.create_table(
        "board_meetings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meeting_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("quorum_required", sa.Integer(), nullable=False),
        sa.Column("quorum_met", sa.Boolean(), nullable=True),
        sa.Column("pack_storage_path", sa.String(512), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_meetings_schedule", "board_meetings", ["entity_id", "scheduled_at", "status"])

    # ── agenda_items ─────────────────────────────────
    op.create_table(
        "agenda_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("board_meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(32), nullable=False, server_default="LOW"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    # ── resolutions ──────────────────────────────────
    op.create_table(
        "resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("board_meetings.id"), nullable=True),
        sa.Column("resolution_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("text_body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("adopted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── meeting_minutes ──────────────────────────────
    op.create_table(
        "meeting_minutes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("board_meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column("final_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── action_items ─────────────────────────────────
    op.create_table(
        "action_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("board_meetings.id"), nullable=True),
        sa.Column("resolution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resolutions.id"), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assigned_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_actions_due", "action_items", ["status", "due_at"])

    # ── powers_of_attorney ───────────────────────────
    op.create_table(
        "powers_of_attorney",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attorney_name", sa.String(255), nullable=False),
        sa.Column("scope_text", sa.Text(), nullable=False),
        sa.Column("subdelegation_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_poa_expiry", "powers_of_attorney", ["status", "expires_at"])

    # ── compliance_obligations ───────────────────────
    op.create_table(
        "compliance_obligations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recurrence_rule", sa.String(128), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("evidence_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_obligations_due", "compliance_obligations", ["status", "due_at"])

    # ── filing_events ────────────────────────────────
    op.create_table(
        "filing_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("compliance_obligations.id"), nullable=True),
        sa.Column("filing_type", sa.String(64), nullable=False),
        sa.Column("filed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("evidence_payload", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_filings_deadline", "filing_events", ["status", "deadline_at"])

    # ── disclosure_events ────────────────────────────
    op.create_table(
        "disclosure_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_disclosures_due", "disclosure_events", ["status", "due_at"])

    # ── ai_analysis_runs ─────────────────────────────
    op.create_table(
        "ai_analysis_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("legal_entities.id"), nullable=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("board_meetings.id"), nullable=True),
        sa.Column("pipeline_type", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("prompt_version", sa.String(32), nullable=False),
        sa.Column("input_snapshot", postgresql.JSON(), nullable=False),
        sa.Column("output_snapshot", postgresql.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("trace_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── audit_events ─────────────────────────────────
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=True),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=True),
        sa.Column("payload", postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_audit_resource", "audit_events", ["resource_type", "resource_id", sa.text("created_at DESC")])


def downgrade() -> None:
    tables = [
        "audit_events", "ai_analysis_runs", "disclosure_events",
        "filing_events", "compliance_obligations", "powers_of_attorney",
        "action_items", "meeting_minutes", "resolutions", "agenda_items",
        "board_meetings", "ownership_links", "corporate_officers",
        "legal_entities", "api_users", "tenants",
    ]
    for t in tables:
        op.drop_table(t)
