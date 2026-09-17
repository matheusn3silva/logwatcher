from dataclasses import dataclass, field

@dataclass
class ConnectionProfile():
    id: str
    name: str
    server: str
    database: str
    username: str
    tables: list[str] = field(default_factory=list)