from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    server: str
    database: str
    username: str
    password: str

