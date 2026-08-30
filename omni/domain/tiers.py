"""Única fonte de verdade pros nomes de tier -- antes desta mudança, a mesma
string literal ("Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B
White-Label)") estava duplicada em auth_service.py, ui/sidebar.py,
ui/panels/config_panels.py e json_organization_repository.py, sem nada
garantindo que ficassem em sincronia -- um typo em qualquer uma delas fazia
`tier_permissions` cair silenciosamente no tier menos privilegiado.

Migrations SQL (migrations/versions/) não conseguem importar isso -- os
valores literais lá precisam ser mantidos manualmente em sincronia com estas
constantes (comentado no próprio arquivo de migration).
"""

FREE = "Free (Lead Magnet)"
STANDARD = "Standard (B2C Trader)"
PREMIUM = "Premium (B2B White-Label)"

ALL_TIERS = (FREE, STANDARD, PREMIUM)
