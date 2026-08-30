"""Portas (interfaces) que a camada de aplicação usa para falar com o mundo externo.

Nenhum destes Protocols importa Streamlit ou bibliotecas de rede — só os adapters
(em omni/adapters) implementam essas portas de fato.

Toda porta "tenant-scoped" (config, credenciais, pools de ativos, logs de ML)
recebe `org_id` explicitamente como primeiro parâmetro real -- é o mecanismo
primário e testável de isolamento multi-tenant (ver omni/domain/tenancy.py e
docs/ARCHITECTURE.md). Row Level Security no Postgres é a segunda camada,
redundante de propósito; nenhuma das duas sozinha é o suficiente.
"""

from typing import Dict, List, Optional, Protocol, Tuple

from omni.domain.models import GlobalCryptoStats, LiquidityData, MarketSentiment, OrgMember, Organization, Quote, User


class MarketDataPort(Protocol):
    def fetch_quotes(self, symbols: Tuple[str, ...], brapi_token: str = "") -> Dict[str, Quote]: ...


class SentimentPort(Protocol):
    def fetch_fear_greed(self) -> MarketSentiment: ...


class GlobalMarketPort(Protocol):
    def fetch_global_stats(self) -> GlobalCryptoStats: ...


class LiquidityDataPort(Protocol):
    def fetch_liquidity_data(self, base_price: float) -> LiquidityData: ...


class ReportExporterPort(Protocol):
    def to_pdf(self, text_content: str, company: str, timestamp: str) -> bytes: ...


class NotificationPort(Protocol):
    def send(self, target: str, message: str, credentials: dict) -> Tuple[bool, str]: ...


class TriggerConfigRepositoryPort(Protocol):
    def save(self, org_id: str, modulo: str, config_data: dict) -> Tuple[bool, str]: ...

    def load(self, org_id: str, modulo: str) -> dict: ...

    def load_all(self, org_id: str) -> Dict[str, dict]: ...

    def mark_dispatched(self, org_id: str, modulo: str, dispatched_at: str) -> None: ...


class AutomationConfigRepositoryPort(Protocol):
    def save(self, org_id: str, config_data: dict) -> Tuple[bool, str]: ...

    def load(self, org_id: str) -> dict: ...


class CredentialsRepositoryPort(Protocol):
    def save(self, org_id: str, config_data: dict) -> Tuple[bool, str]: ...

    def load(self, org_id: str) -> dict: ...


class UserRepositoryPort(Protocol):
    """Identidade é global, não por organização -- a mesma pessoa pode
    pertencer a mais de uma organização (ver OrgMemberRepositoryPort)."""

    def create_user(self, email: str, password_hash: str, tier: str) -> User: ...

    def get_by_email(self, email: str) -> Optional[User]: ...

    def update_password_hash(self, user_id: int, new_hash: str) -> None: ...


class OrganizationRepositoryPort(Protocol):
    def create_organization(self, name: str, slug: str, tier: str) -> Organization: ...

    def get_by_id(self, org_id: str) -> Optional[Organization]: ...

    def get_by_slug(self, slug: str) -> Optional[Organization]: ...

    def update(self, org_id: str, fields: dict) -> None: ...

    def list_active_org_ids(self) -> List[str]: ...


class OrgMemberRepositoryPort(Protocol):
    def add_member(self, org_id: str, user_id: int, role: str) -> OrgMember: ...

    def get_role(self, org_id: str, user_id: int) -> Optional[str]: ...

    def list_members(self, org_id: str) -> List[OrgMember]: ...

    def list_orgs_for_user(self, user_id: int) -> List[OrgMember]: ...


class AssetPoolRepositoryPort(Protocol):
    def load_pool(self, org_id: str, modulo: str) -> Optional[list]: ...

    def save_pool(self, org_id: str, modulo: str, pool: list) -> None: ...

    def load_categories(self, org_id: str, modulo: str) -> Optional[dict]: ...

    def save_categories(self, org_id: str, modulo: str, categories: dict) -> None: ...


class MlPredictionLogRepositoryPort(Protocol):
    def load_all(self, org_id: str) -> List[dict]: ...

    def append(self, org_id: str, entry: dict) -> None: ...


class EmailPort(Protocol):
    def send(self, to_addresses: List[str], subject: str, body: str) -> Tuple[bool, str]: ...


class WebhookPort(Protocol):
    def post(self, url: str, payload: dict, auth_token: str = "") -> Tuple[bool, str]: ...
