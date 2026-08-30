"""Constante única usada pela transição single-tenant -> multi-tenant.

`ui/` (Streamlit) não tem noção de "organização" -- é uma interface pensada
pra um usuário só, herdada da era pré-multi-tenant. Em vez de reescrever a UI
inteira pra ganhar esse conceito agora, toda chamada vinda de `ui/` passa essa
organização fixa e conhecida como `org_id`. Isso é deliberado e temporário: o
plano é que `ui/` (ou o que restar dela) seja descomissionada antes da Fase 2
ligar Row Level Security de verdade -- ver docs/ARCHITECTURE.md.
"""

LEGACY_ORG_ID = "00000000-0000-0000-0000-000000000001"
