from dataclasses import dataclass

@dataclass
class LogTable:
    schema: str
    name: str
    rows: int
    total_mb: float
    used_mb: float