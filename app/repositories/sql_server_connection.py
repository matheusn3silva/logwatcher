import mssql_python

from app.config.database_config import DatabaseConfig

class SQLServerConnection:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._connection = None

    def connect(self):
        if self._connection is not None:
            return self._connection

        username = (
            self._config.sa_username
            if self._config.use_sa and self._config.sa_username
            else self._config.username
        )

        password = (
            self._config.sa_password
            if self._config.use_sa and self._config.sa_password
            else self._config.password
        )

        connection_string = (
            f"Server={self._config.server};"
            f"Database={self._config.database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

        self._connection = mssql_python.connect(connection_string)

        return self._connection

    def disconnect(self):
        if (self._connection is not None):
            self._connection.close()
            self._connection = None

    def test_connection(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()

            return version[0]

        finally:
            self.disconnect()