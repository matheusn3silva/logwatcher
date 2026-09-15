from dataclasses import dataclass

from app.models.log_table import LogTable

@dataclass
class DashboardSummary:
    tables: list[LogTable]
    total_tables: int
    total_rows: int
    total_space_mb: float
    used_space_mb: float

