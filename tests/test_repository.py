from app.config.database_config import DatabaseConfig
from app.repositories.sql_server_connection import SQLServerConnection
from app.repositories.log_repository import LogRepository

config = DatabaseConfig(
    server="localhost",
    database="suricato",
    username="suricato",
    password="suricato"
)

connection = SQLServerConnection(config)
repository = LogRepository(connection)

print("Arquivos de log:")
print(repository.get_log_files())

print("\nTabelas:")
for table in repository.get_table_sizes()[:5]:
    print(table)

connection.disconnect()