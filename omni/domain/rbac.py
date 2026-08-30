"""RBAC dentro de uma organização -- eixo ortogonal ao tier de billing.

`catalog_service.tier_permissions(tier)` responde "o plano da empresa permite
isso?" (Free/Standard/Premium). `role_capabilities(role)` responde "essa
pessoa, dentro da empresa dela, tem permissão de fazer isso?" (owner/admin/
analyst/viewer). As duas checagens são independentes e ambas precisam passar
-- um `analyst` numa organização Premium não vira admin por causa do plano.
"""

from dataclasses import dataclass

ROLES = ("owner", "admin", "analyst", "viewer")


@dataclass(frozen=True)
class RoleCapabilities:
    can_manage_members: bool
    can_manage_billing: bool
    can_manage_credentials: bool
    can_edit_triggers: bool
    can_edit_automations: bool
    can_edit_asset_pools: bool


_VIEWER = RoleCapabilities(
    can_manage_members=False, can_manage_billing=False, can_manage_credentials=False,
    can_edit_triggers=False, can_edit_automations=False, can_edit_asset_pools=False,
)
_ANALYST = RoleCapabilities(
    can_manage_members=False, can_manage_billing=False, can_manage_credentials=False,
    can_edit_triggers=True, can_edit_automations=True, can_edit_asset_pools=True,
)
_ADMIN = RoleCapabilities(
    can_manage_members=True, can_manage_billing=False, can_manage_credentials=True,
    can_edit_triggers=True, can_edit_automations=True, can_edit_asset_pools=True,
)
_OWNER = RoleCapabilities(
    can_manage_members=True, can_manage_billing=True, can_manage_credentials=True,
    can_edit_triggers=True, can_edit_automations=True, can_edit_asset_pools=True,
)

_BY_ROLE = {"owner": _OWNER, "admin": _ADMIN, "analyst": _ANALYST, "viewer": _VIEWER}


def role_capabilities(role: str) -> RoleCapabilities:
    """Papel desconhecido/vazio é tratado como o menos privilegiado (viewer),
    nunca como o mais privilegiado -- falha segura."""
    return _BY_ROLE.get(role, _VIEWER)
