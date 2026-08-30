from omni.adapters.persistence.postgres.single_row_repository import SingleRowPerOrgRepository


class PostgresCredentialsRepository(SingleRowPerOrgRepository):
    """Uma linha por organização. Guarda credenciais de terceiros (BRAPI,
    WhatsApp, Telegram) de cada cliente -- candidato natural a criptografia em
    repouso (ver docs/ARCHITECTURE.md, Fase 2), ainda não implementada nesta
    camada. Ver SingleRowPerOrgRepository para a lógica compartilhada com
    PostgresAutomationConfigRepository."""

    def __init__(self):
        super().__init__(
            table_name="api_credentials",
            success_message="Credenciais salvas com sucesso!",
            error_message_prefix="Falha ao gravar credenciais",
        )
