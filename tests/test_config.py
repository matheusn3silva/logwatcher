from app.config.database_config import DatabaseConfig

config = DatabaseConfig(
    server="localhost",
    database="suricato",
    username="suricato",
    password="suricato"
)

print(config)
print(config.server)
print(config.database)
