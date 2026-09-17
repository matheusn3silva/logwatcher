from app.repositories.sql_server_connection import SQLServerConnection
from app.models.log_table import LogTable
from app.models.log_file import LogFile
from app.models.database_status import DatabaseStatus

class LogRepository:
    def __init__(self, connection: SQLServerConnection):
        self._connection = connection

    def get_log_files(self):
        conn = self._connection.connect()
        cursor = conn.cursor()

        query = """
        SELECT
            name AS LogicalName,
            size * 8.0 / 1024 AS SizeMB,
            FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024 AS UsedMB
        FROM sys.database_files
        WHERE type_desc = 'LOG';
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return [
            LogFile(
                logical_name=row[0],
                size_mb=row[1],
                used_mb=row[2]
            )
            for row in rows
        ]

    def get_database_status(self) -> DatabaseStatus:
        conn = self._connection.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                name,
                recovery_model_desc,
                log_reuse_wait_desc
            FROM sys.databases
            WHERE name = DB_NAME()
        """)

        row = cursor.fetchone()
        cursor.close()

        return DatabaseStatus(
            database_name=row[0],
            recovery_model=row[1],
            log_reuse_wait=row[2]
        )

    def get_table_sizes(self, table_names: list[str]) -> list[LogTable]:
        if not table_names:
            return []

        conn = self._connection.connect()
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in table_names)

        query = f"""
        SELECT
            t.name,
            s.name,
            SUM(p.rows) AS RowCounts,
            SUM(a.total_pages) * 8.0 / 1024 AS TotalSpaceMB,
            SUM(a.used_pages) * 8.0 / 1024 AS UsedSpaceMB
        FROM sys.tables t
        JOIN sys.indexes i
            ON t.object_id = i.object_id
        JOIN sys.partitions p
            ON i.object_id = p.object_id
                AND i.index_id = p.index_id
        JOIN sys.allocation_units a
            ON p.partition_id = a.container_id
        JOIN sys.schemas s
            ON t.schema_id = s.schema_id
        WHERE t.name in ({placeholders})
        GROUP BY t.name, s.name
        ORDER BY TotalSpaceMB DESC
        """

        cursor.execute(query, tuple(table_names))

        rows = cursor.fetchall()
        cursor.close()

        return [
            LogTable(
                name=row[0],
                schema=row[1],
                rows=row[2],
                total_mb=row[3],
                used_mb=row[4]
            )
            for row in rows
        ]

    def truncate_table(self, schema: str, table: str) -> None:
        query = f"TRUNCATE TABLE [{schema}].[{table}]"

        self._connection.execute(query)

    def delete_table(self, schema: str, table: str) -> None:
        query = f"DELETE [{schema}].[{table}]"

        self._connection.execute(query)

    def shrink_log_file(self, logical_name: str):
        query = f"""
            DBCC SHRINKFILE (
                [{logical_name}],
                0
            )
        """

        self._connection.execute_dbcc(query)

    