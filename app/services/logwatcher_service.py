from app.models.dashboard_summary import DashboardSummary
from app.repositories.log_repository import LogRepository
from app.services.table_parser import TableParser
from app.utils.audit_logger import AuditLogger
from app.models.shrink_result import ShrinkResult

class LogWatcherService:
    def __init__(self, repository: LogRepository, profile_name: str = "-"):
        self._repository = repository
        self._profile_name = profile_name

    def analyze_database(self, tables_text: str) -> DashboardSummary:
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
        
    def validate_tables(self, tables_text: str):
        tables = TableParser.parse(tables_text)
        return self._repository.validate_tables(tables)

    def truncate_monitored_table(self, summary, index: int):
        if index < 0 or index >= len(summary.tables):
            raise ValueError("Tabela inválida.")

        table = summary.tables[index]
        table_name = f"{table.schema}.{table.name}"

        try:
            self._repository.truncate_table(table.schema, table.name)
        except Exception as error:
            self._log(f"Falha ao truncar {table_name}: {error}",
                       action="TRUNCATE", status="ERRO")
            raise

        self._log(f"Tabela {table_name} truncada com sucesso.", action="TRUNCATE")
        return table

    def delete_monitored_table(self, summary, index: int):
        if index < 0 or index >= len(summary.tables):
            raise ValueError("Tabela inválida.")

        table = summary.tables[index]
        table_name = f"{table.schema}.{table.name}"

        try:
            self._repository.delete_table(table.schema, table.name)
        except Exception as error:
            self._log(f"Falha ao executar DELETE em {table_name}: {error}",
                       action="DELETE", status="ERRO")
            raise

        self._log(f"DELETE executado em {table_name}.", action="DELETE")
        return table

    def shrink_log(self, index: int) -> ShrinkResult:
        logs = self._repository.get_log_files()
        if index < 0 or index >= len(logs):
            raise ValueError("Log inválido.")

        log = logs[index]
        before = log.size_mb

        try:
            self._repository.shrink_log_file(log.logical_name)
        except Exception as error:
            self._log(f"Falha ao executar SHRINK em {log.logical_name}: {error}",
                       action="SHRINK_LOG", status="ERRO")
            raise

        updated_logs = self._repository.get_log_files()
        after = updated_logs[index].size_mb if index < len(updated_logs) else before

        self._log(
            f"SHRINK em {log.logical_name}: {before:.2f} MB -> {after:.2f} MB "
            f"(recuperado {before - after:.2f} MB).",
            action="SHRINK_LOG",
        )
        return ShrinkResult(log.logical_name, before, after)

    def shrink_data(self, index: int) -> ShrinkResult:
        data_files = self._repository.get_data_files()

        if index < 0 or index >= len(data_files):
            raise ValueError("Arquivo de dados inválido.")

        data_file = data_files[index]
        before = data_file.size_mb

        self._repository.shrink_data_file(data_file.logical_name)

        updated_files = self._repository.get_data_files()
        after = updated_files[index].size_mb if index < len(updated_files) else before

        self._log(f"Realizou SHRINK no arquivo de dados {data_file.logical_name}.")

        return ShrinkResult(data_file.logical_name, before, after)

    def get_data_status(self):
        status = self._repository.get_database_status()
        data_files = self._repository.get_data_files()

        return status, data_files

    def get_log_status(self):
        status = self._repository.get_database_status()
        logs = self._repository.get_log_files()

        return status, logs

    def _log(self, message: str, action: str = "-", status: str = "SUCESSO") -> None:
        try:
            AuditLogger.log(
                database=self._repository.database,
                username=self._repository.username,
                message=message,
                profile=self._profile_name,
                action=action,
                status=status,
            )
        except Exception:
            pass
    