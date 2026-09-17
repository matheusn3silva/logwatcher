import json
from pathlib import Path
from uuid import uuid4

from app.models.connection_profile import ConnectionProfile

class ConnectionProfileService:
    def __init__(self):
        self._data_dir = Path("data")
        self._file = self._data_dir / "connections.json"

        self._data_dir.mkdir(exist_ok=True)

    def load_profiles(self) -> list[ConnectionProfile]:
        if not self._file.exists():
            return []

        if self._file.stat().st_size == 0:
            return []

        try:
            with open(self._file, "r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError:
            return []

        return [
            ConnectionProfile(**profile)
            for profile in data.get("profiles", [])
        ]

    def save_profiles(self, profiles: list[ConnectionProfile]):
        data = {
            "profiles": [
                profile.__dict__
                for profile in profiles
            ]
        }

        with open(self._file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def create_profile(
        self,
        name: str,
        server: str,
        database: str,
        username: str,
        tables: list[str]
    ):
        profiles = self.load_profiles()

        profiles.append(
            ConnectionProfile(
                id=str(uuid4()),
                name=name,
                server=server,
                database=database,
                username=username,
                tables=tables
            )
        )

        self.save_profiles(profiles)

    def delete_profile(self, profile_id: str):
        profiles = [
            profile
                for profile in self.load_profiles()
                if profile.id != profile_id
            ]

        self.save_profiles(profiles)

    def get_profile(self, profile_id: str):
        for profile in self.load_profiles():
            if profile.id == profile_id:
                return profile

        return None

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
            if profile.id == profile_id:
                profile.name = name
                profile.server = server
                profile.database = database
                profile.username = username
                profile.tables = tables
                break

        self.save_profiles(profiles)