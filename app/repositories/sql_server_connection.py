import mssql_python

from app.config.database_config import DatabaseConfig

class SQLServerConnection:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._connection = None

    def connect(self):
        if self._connection is not None:
            return self._connection

        connection_string = (
            f"Server={self._config.server};"
            f"Database={self._config.database};"
            f"UID={self._config.username};"
            f"PWD={self._config.password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

        self._connection = mssql_python.connect(connection_string)

        return self._connection

    def disconnect(self):
        if (self._connection is not None):
            self._connection.close()
            self._connection = None

    def test_connection(self) -> str:
        conn = self.connect()
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
                    
        version = cursor.fetchone()
        
        return version[0]

    def execute(self, query: str, params: tuple = ()) -> None:
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)
            conn.commit()
        except: 
            conn.rollback()
            raise

    def execute_dbcc(self, query: str, params: tuple = ()):
        conn = self.connect()

        previous_autocommit = conn.autocommit

        try:
            conn.autocommit = True

            cursor = conn.cursor()
            cursor.execute(query, params)
            cursor.close()

        finally:
            conn.autocommit = previous_autocommit