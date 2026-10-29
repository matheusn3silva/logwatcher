from app.config.database_config import DatabaseConfig
from app.repositories.log_repository import LogRepository
from app.repositories.sql_server_connection import SQLServerConnection
from app.utils.audit_logger import AuditLogger


class ConnectionService:

    def __init__(self):
        self._connection = None
        self._repository = None
        self._profile_name = "-"

    def connect(self, config: DatabaseConfig, profile_name: str = "-"):
        self._profile_name = profile_name or "-"
        self._connection = SQLServerConnection(config)

        try:
            version = self._connection.test_connection()
        except Exception as error:
            self._log(
                f"Falha ao conectar em {config.server}/{config.database}: {error}",
                action="LOGIN", status="ERRO",
                database=config.database, username=config.username,
            )
            raise

        self._repository = LogRepository(self._connection)

        self._log(
            f"Conexão estabelecida com {config.server}/{config.database}.",
            action="LOGIN",
            database=config.database, username=config.username,
        )

        return version

    @property
    def repository(self):
        return self._repository

    def disconnect(self):
        if self._connection:
            database = self._connection.database
            username = self._connection.username

            self._connection.disconnect()

            self._log(
                f"Desconectado de {database}.",
                action="LOGOUT",
                database=database, username=username,
            )

    def _log(self, message, action, database, username, status="SUCESSO"):
        try:
            AuditLogger.log(
                database=database,
                username=username,
                message=message,
                profile=self._profile_name,
                action=action,
                status=status,
            )
        except Exception:
            pass