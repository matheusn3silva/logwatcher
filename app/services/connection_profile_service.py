import json
from pathlib import Path
from uuid import uuid4

from app.models.connection_profile import ConnectionProfile


class ConnectionProfileService:

    def __init__(self):
        self._data_dir = Path("data")
        self._file = self._data_dir / "connections.json"

        self._data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ==========================================================
    # LEITURA
    # ==========================================================

    def load_profiles(self) -> list[ConnectionProfile]:
        if not self._file.exists():
            return []

        if self._file.stat().st_size == 0:
            return []

        try:
            with open(
                self._file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

        profiles = data.get("profiles", [])

        if not isinstance(profiles, list):
            return []

        result = []

        for profile in profiles:
            if not isinstance(profile, dict):
                continue

            try:
                result.append(
                    ConnectionProfile(**profile)
                )
            except TypeError:
                continue

        return result

    # ==========================================================
    # GRAVAÇÃO
    # ==========================================================

    def save_profiles(
        self,
        profiles: list[ConnectionProfile]
    ):
        self._data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "profiles": [
                profile.__dict__
                for profile in profiles
            ]
        }

        with open(
            self._file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ==========================================================
    # CRIAÇÃO
    # ==========================================================

    def create_profile(
        self,
        name: str,
        server: str,
        database: str,
        username: str,
        tables: list[str]
    ):
        profiles = self.load_profiles()

        normalized_tables = self._normalize_tables(tables)

        profile = ConnectionProfile(
            id=str(uuid4()),
            name=name.strip(),
            server=server.strip(),
            database=database.strip(),
            username=username.strip(),
            tables=normalized_tables
        )

        profiles.append(profile)

        self.save_profiles(profiles)

        return profile

    # ==========================================================
    # ATUALIZAÇÃO
    # ==========================================================

    def update_profile(
        self,
        profile_id: str,
        name: str,
        server: str,
        database: str,
        username: str,
        tables: list[str]
    ):
        profiles = self.load_profiles()

        for profile in profiles:
            if profile.id != profile_id:
                continue

            profile.name = name.strip()
            profile.server = server.strip()
            profile.database = database.strip()
            profile.username = username.strip()

            profile.tables = self._merge_tables(
                current_tables=profile.tables,
                new_tables=tables
            )

            self.save_profiles(profiles)

            return profile

        raise ValueError(
            "Perfil de conexão não encontrado."
        )

    # ==========================================================
    # EXCLUSÃO
    # ==========================================================

    def delete_profile(
        self,
        profile_id: str
    ):
        profiles = self.load_profiles()

        filtered_profiles = [
            profile
            for profile in profiles
            if profile.id != profile_id
        ]

        if len(filtered_profiles) == len(profiles):
            raise ValueError("Perfil de conexão não encontrado.")

        self.save_profiles(filtered_profiles)

    # ==========================================================
    # CONSULTA
    # ==========================================================

    def get_profile(
        self,
        profile_id: str
    ):
        for profile in self.load_profiles():
            if profile.id == profile_id:
                return profile

        return None

    # ==========================================================
    # TABELAS
    # ==========================================================

    @staticmethod
    def _normalize_tables(
        tables: list[str]
    ) -> list[str]:

        if not tables:
            return []

        result = []
        existing = set()

        for table in tables:
            if not isinstance(table, str):
                continue

            table = table.strip()
            if not table:
                continue

            key = table.casefold()
            if key in existing:
                continue

            existing.add(key)
            result.append(table)

        return result

    @classmethod
    def _merge_tables(
        cls,
        current_tables: list[str],
        new_tables: list[str]
    ) -> list[str]:
        current = cls._normalize_tables(current_tables)

        new = cls._normalize_tables(new_tables)

        result = current.copy()
        existing = {
            table.casefold()
            for table in result
        }

        for table in new:
            key = table.casefold()

            if key in existing:
                continue

            result.append(table)
            existing.add(key)

        return result