from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    server: str
    database: str
    username: str
    password: str
    use_sa: bool = False
    sa_username: str | None = None
    sa_password: str | None = None

