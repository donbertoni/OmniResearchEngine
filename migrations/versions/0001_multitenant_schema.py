"""Multi-tenant schema baseline.

Substitui completamente o antigo omni/adapters/persistence/postgres/schema.sql
(aplicado via ensure_schema() a cada boot) por uma migration versionada.
Como não existe nenhum deploy real em produção ainda (o app roda em fallback
JSON local até uma DATABASE_URL dedicada ser configurada -- ver
docs/ARCHITECTURE.md), esta é a única migration: já nasce multi-tenant, sem
precisar de uma segunda migration de "backfill" para dados que não existem.

Revision ID: 0001
Revises:
Create Date: 2026-08-29
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Organização "legado" usada por toda chamada vinda de ui/ (Streamlit não tem
# conceito de organização) -- ver omni/domain/tenancy.py::LEGACY_ORG_ID.
LEGACY_ORG_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(
        """
        CREATE TABLE organizations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            tier TEXT NOT NULL DEFAULT 'Free (Lead Magnet)',
            subscription_status TEXT NOT NULL DEFAULT 'trialing',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            company_name TEXT,
            cnpi_code TEXT,
            logo_url TEXT,
            primary_color TEXT,
            custom_domain TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'Standard (B2C Trader)',
            email_verified_at TIMESTAMPTZ,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE org_members (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK (role IN ('owner','admin','analyst','viewer')),
            invited_by INTEGER REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (org_id, user_id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE user_identities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            provider TEXT NOT NULL,
            provider_subject TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (provider, provider_subject)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE refresh_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            replaced_by UUID REFERENCES refresh_tokens(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE password_reset_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE email_verification_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE trigger_configs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            modulo TEXT NOT NULL,
            config JSONB NOT NULL,
            last_dispatched_at TEXT,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (org_id, modulo)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE automation_settings (
            org_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
            config JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE api_credentials (
            org_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
            config JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE asset_pools (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            modulo TEXT NOT NULL,
            pool JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (org_id, modulo)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE asset_categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            modulo TEXT NOT NULL,
            categories JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (org_id, modulo)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE ml_prediction_logs (
            id SERIAL PRIMARY KEY,
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            ts_label TEXT NOT NULL,
            asset TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE audit_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id),
            action TEXT NOT NULL,
            details JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # Organização "legado" usada por toda chamada vinda de ui/ (Streamlit) até
    # a Fase 1 substituir a UI -- ver omni/domain/tenancy.py.
    op.execute(
        f"""
        INSERT INTO organizations (id, name, slug, tier)
        VALUES ('{LEGACY_ORG_ID}', 'Legacy (Streamlit)', 'legacy-streamlit', 'Standard (B2C Trader)')
        """
    )


def downgrade() -> None:
    for table in (
        "audit_log", "ml_prediction_logs", "asset_categories", "asset_pools",
        "api_credentials", "automation_settings", "trigger_configs",
        "email_verification_tokens", "password_reset_tokens", "refresh_tokens",
        "user_identities", "org_members", "users", "organizations",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
