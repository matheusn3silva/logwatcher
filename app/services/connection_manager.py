from app.config.database_config import DatabaseConfig
from app.services.connection_service import ConnectionService
from app.services.logwatcher_service import LogWatcherService


class ConnectionManager:
    def __init__(self):
        self._connections = {}

    def connect(self, profile, password):

        if profile.id in self._connections:
            return self._connections[profile.id]["logwatcher"]

        config = DatabaseConfig(
            server=profile.server,
            database=profile.database,
            username=profile.username,
            password=password
        )

        connection_service = ConnectionService()

        try:
            connection_service.connect(config)

            logwatcher_service = LogWatcherService(
                connection_service.repository,
                profile_name=profile.name,
            )

            if profile.tables:
                tables_text = ",".join(profile.tables)

                valid, invalid = logwatcher_service.validate_tables(tables_text)

                if invalid:
                    invalid_tables = ", ".join(invalid)

                    raise ValueError(
                        f"As seguintes tabelas não foram encontradas: "
                        f"{invalid_tables}"
                    )

            self._connections[profile.id] = {
                "profile": profile,
                "connection": connection_service,
                "logwatcher": logwatcher_service
            }

            return logwatcher_service

        except Exception:
            connection_service.disconnect()
            raise

    def disconnect(self, profile_id):
        connection = self._connections.pop(profile_id, None)

        if connection:
            connection["connection"].disconnect()

    def is_connected(self, profile_id):
        return profile_id in self._connections

    def get_service(self, profile_id):
        connection = self._connections.get(profile_id)

        if not connection:
            return None

        return connection["logwatcher"]

    def get_connection(self, profile_id):
        connection = self._connections.get(profile_id)

        if not connection:
            return None

        return connection["connection"]

    def get_connected_profiles(self):
        return [
            connection["profile"]
            for connection in self._connections.values()
        ]

    def disconnect_all(self):
        for profile_id in list(self._connections.keys()):
            self.disconnect(profile_id)