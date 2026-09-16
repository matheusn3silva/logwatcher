from app.config.database_config import DatabaseConfig
from app.repositories.log_repository import LogRepository
from app.repositories.sql_server_connection import SQLServerConnection

class ConnectionService:

    def __init__(self):
        self._connection = None
        self._repository = None

    def connect(self, config: DatabaseConfig):
        self._connection = SQLServerConnection(config)

        version = self._connection.test_connection()

        self._repository = LogRepository(self._connection)

        return version

    @property
    def repository(self):
        return self._repository

    def disconnect(self):
        if self._connection:
            self._connection.disconnect()