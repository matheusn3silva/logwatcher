from app.config.database_config import DatabaseConfig
from app.repositories.sql_server_connection import SQLServerConnection

config = DatabaseConfig(
    server="localhost\\SQLEXPRESS01",
    database="suricato",
    username="suricato",
    password="suricato"
)

connection = SQLServerConnection(config)

print(connection.test_connection())