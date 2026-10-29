from dataclasses import dataclass

from app.models.log_table import LogTable
from app.models.log_file import LogFile
from app.models.data_file import DataFile

@dataclass
class DashboardSummary:
    tables: list[LogTable]
    logs: list[LogFile]
    data_files: list[DataFile]

    total_tables: int
    total_rows: int

    total_space_mb: float
    used_space_mb: float

    total_log_size_mb: float
    total_log_used_mb: float

    total_data_size_mb: float
    total_data_used_mb: float