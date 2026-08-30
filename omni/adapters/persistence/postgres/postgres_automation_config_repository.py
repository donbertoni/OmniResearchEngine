from omni.adapters.persistence.postgres.single_row_repository import SingleRowPerOrgRepository


class PostgresAutomationConfigRepository(SingleRowPerOrgRepository):
    """Uma linha por organização. Ver SingleRowPerOrgRepository para a lógica
    compartilhada com PostgresCredentialsRepository."""

    def __init__(self):
        super().__init__(
            table_name="automation_settings",
            success_message="Automações salvas com sucesso!",
            error_message_prefix="Falha ao gravar automações",
        )
