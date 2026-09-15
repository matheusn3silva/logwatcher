from app.repositories.sql_server_connection import SQLServerConnection

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

        return rows

    def get_table_sizes(self):
        conn = self._connection.connect()

        cursor = conn.cursor()

        query = """
        SELECT
            t.name AS TableName,
            s.name AS SchemaName,
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
        WHERE t.is_ms_shipped = 0
        GROUP BY t.name, s.name
        ORDER BY TotalSpaceMB DESC;
        """

        cursor.execute(query)

        return cursor.fetchall()