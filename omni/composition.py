"""Composition root único do projeto: o único lugar que instancia adapters
concretos, para que tanto o processo interativo do Streamlit (app.py) quanto o
worker headless do scheduler (scheduler_worker.py) montem exatamente a mesma
infraestrutura -- Postgres quando DATABASE_URL está configurada, fallback local
em JSON caso contrário. Nenhum outro módulo deve importar um adapter concreto
diretamente.

Schema Postgres gerenciado por Alembic (`alembic upgrade head`), não mais
aplicado aqui em runtime -- ver migrations/ na raiz do projeto.
"""

import logging
from dataclasses import dataclass
from typing import Any

from omni.adapters.global_market.coingecko_adapter import CoinGeckoGlobalMarketAdapter
from omni.adapters.liquidity.deribit_orderbook_adapter import DeribitLiquidityAdapter
from omni.adapters.liquidity.es_futures_volume_profile_adapter import EsFuturesLiquidityAdapter
from omni.adapters.market_data.brapi_adapter import BrapiMarketDataAdapter
from omni.adapters.market_data.composite_adapter import CompositeMarketDataAdapter
from omni.adapters.market_data.yfinance_adapter import YFinanceMarketDataAdapter
from omni.adapters.notifications.smtp_email_adapter import SmtpEmailAdapter
from omni.adapters.notifications.telegram_adapter import TelegramNotificationAdapter
from omni.adapters.notifications.webhook_adapter import GenericWebhookAdapter
from omni.adapters.notifications.whatsapp_adapter import WhatsAppNotificationAdapter
from omni.adapters.persistence import (
    json_asset_pool_repository,
    json_automation_config_repository,
    json_credentials_repository,
    json_ml_log_repository,
    json_organization_repository,
    json_org_member_repository,
    json_trigger_config_repository,
    json_user_repository,
)
from omni.adapters.persistence.postgres import connection as postgres_connection
from omni.adapters.persistence.postgres.postgres_asset_pool_repository import PostgresAssetPoolRepository
from omni.adapters.persistence.postgres.postgres_automation_config_repository import PostgresAutomationConfigRepository
from omni.adapters.persistence.postgres.postgres_credentials_repository import PostgresCredentialsRepository
from omni.adapters.persistence.postgres.postgres_ml_log_repository import PostgresMlLogRepository
from omni.adapters.persistence.postgres.postgres_organization_repository import PostgresOrganizationRepository
from omni.adapters.persistence.postgres.postgres_org_member_repository import PostgresOrgMemberRepository
from omni.adapters.persistence.postgres.postgres_trigger_config_repository import PostgresTriggerConfigRepository
from omni.adapters.persistence.postgres.postgres_user_repository import PostgresUserRepository
from omni.adapters.reporting.pdf_reportlab_adapter import ReportLabPdfExporter
from omni.adapters.sentiment.alternative_me_adapter import AlternativeMeSentimentAdapter
from omni.config.settings import AppSettings, load_settings

logger = logging.getLogger(__name__)


@dataclass
class Infrastructure:
    settings: AppSettings
    market_data_port: Any
    sentiment_port: Any
    global_market_port: Any
    crypto_liquidity_port: Any
    tradfi_liquidity_port: Any
    pdf_exporter_port: Any
    trigger_repo: Any
    automation_repo: Any
    credentials_repo: Any
    user_repo: Any
    org_repo: Any
    org_member_repo: Any
    asset_pool_repo: Any
    ml_log_repo: Any
    webhook_port: Any
    email_port: Any
    whatsapp_port: Any
    telegram_port: Any
    using_postgres: bool


def build_infrastructure() -> Infrastructure:
    settings = load_settings()
    yfinance_adapter = YFinanceMarketDataAdapter()
    brapi_adapter = BrapiMarketDataAdapter()

    using_postgres = postgres_connection.is_configured()
    if using_postgres:
        trigger_repo = PostgresTriggerConfigRepository()
        automation_repo = PostgresAutomationConfigRepository()
        credentials_repo = PostgresCredentialsRepository()
        user_repo = PostgresUserRepository()
        org_repo = PostgresOrganizationRepository()
        org_member_repo = PostgresOrgMemberRepository()
        asset_pool_repo = PostgresAssetPoolRepository()
        ml_log_repo = PostgresMlLogRepository()
        logger.info("Infrastructure: using Postgres persistence (DATABASE_URL configured).")
    else:
        trigger_repo = json_trigger_config_repository.JsonTriggerConfigRepository()
        automation_repo = json_automation_config_repository.JsonAutomationConfigRepository()
        credentials_repo = json_credentials_repository.JsonCredentialsRepository()
        user_repo = json_user_repository.JsonUserRepository()
        org_repo = json_organization_repository.JsonOrganizationRepository()
        org_member_repo = json_org_member_repository.JsonOrgMemberRepository()
        asset_pool_repo = json_asset_pool_repository.JsonAssetPoolRepository()
        ml_log_repo = json_ml_log_repository.JsonMlLogRepository()
        logger.warning("Infrastructure: DATABASE_URL not set, falling back to local JSON files (state won't survive a fresh deploy).")

    return Infrastructure(
        settings=settings,
        market_data_port=CompositeMarketDataAdapter(yfinance_adapter, brapi_adapter),
        sentiment_port=AlternativeMeSentimentAdapter(),
        global_market_port=CoinGeckoGlobalMarketAdapter(),
        crypto_liquidity_port=DeribitLiquidityAdapter(),
        tradfi_liquidity_port=EsFuturesLiquidityAdapter(yfinance_adapter),
        pdf_exporter_port=ReportLabPdfExporter(),
        trigger_repo=trigger_repo,
        automation_repo=automation_repo,
        credentials_repo=credentials_repo,
        user_repo=user_repo,
        org_repo=org_repo,
        org_member_repo=org_member_repo,
        asset_pool_repo=asset_pool_repo,
        ml_log_repo=ml_log_repo,
        webhook_port=GenericWebhookAdapter(),
        email_port=SmtpEmailAdapter(
            host=settings.smtp_host,
            port=settings.smtp_port,
            user=settings.smtp_user,
            password=settings.smtp_password,
            from_addr=settings.smtp_from,
            use_tls=settings.smtp_use_tls,
        ),
        whatsapp_port=WhatsAppNotificationAdapter(base_url=settings.whatsapp_api_base_url),
        telegram_port=TelegramNotificationAdapter(),
        using_postgres=using_postgres,
    )
