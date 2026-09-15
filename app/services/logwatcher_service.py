from app.models.dashboard_summary import DashboardSummary
from app.repositories.log_repository import LogRepository
from app.services.table_parser import TableParser

class LogWatcherService:
    def __init__(self, repository: LogRepository):
        self._repository = repository

    def analyze_tables(self, tables_text: str) -> DashboardSummary:
        table_names = TableParser.parse(tables_text)

        tables = self._repository.get_table_sizes(table_names)
        total_rows = sum(table.rows for table in tables)
        total_space = sum(table.total_mb for table in tables)
        used_space = sum(table.used_mb for table in tables)

        logs = self._repository.get_log_files()
        total_log_size = sum(log.size_mb for log in logs)
        total_log_used = sum(log.used_mb for log in logs)

        return DashboardSummary(
            tables=tables,
            logs=logs,

            total_tables=len(tables),
            total_rows=total_rows,

            total_space_mb=total_space,
            used_space_mb=used_space,

            total_log_size_mb=total_log_size,
            total_log_used_mb=total_log_used
        )