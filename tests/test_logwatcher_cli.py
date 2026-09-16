from app.config.database_config import DatabaseConfig
from app.repositories.sql_server_connection import SQLServerConnection
from app.repositories.log_repository import LogRepository
from app.services.logwatcher_service import LogWatcherService
from tabulate import tabulate

def main():
    print("=" * 50)
    print("LogWatcher - Teste via Terminal")
    print("=" * 50)

    server = input("Servidor: ")
    database = input("Nome do Banco: ")
    username = input("Usuário: ")
    password = input("Senha: ")

    config = DatabaseConfig(
        server=server,
        database=database,
        username=username,
        password=password
    )

    connection = SQLServerConnection(config)
    repository = LogRepository(connection)

    service = LogWatcherService(repository)

    try:
        print("\nConectando...")

        version = connection.test_connection()
        print("Conectado com sucesso!")
        print(f"SQL Server: {version.splitlines()[0]}")

        tables_text = input(
            "\nDigite as tabelas separadas por vírgula: "
        )

        summary = service.analyze_database(tables_text)

        # ---------------- LOGS ----------------
        print("\nArquivos de Log")
        print("-" * 70)

        log_data = [
            [
                log.logical_name,
                f"{log.size_mb:.2f}",
                f"{log.used_mb:.2f}",
                f"{log.free_mb:.2f}"
            ]
            for log in summary.logs
        ]

        print(tabulate(
            log_data,
            headers=["Arquivo", "Espaço reservado MB", "Usado MB", "Livre MB"],
            tablefmt="grid"
        ))

        # ---------------- TABELAS ----------------
        print("\nTabelas Monitoradas")
        print("-" * 70)

        table_data = [
            [
                table.name,
                f"{table.rows:,}",
                f"{table.total_mb:.2f}",
                f"{table.used_mb:.2f}",
            ]
            for table in summary.tables
        ]

        print(tabulate(
            table_data,
            headers=["Tabela", "Linhas", "Espaço Reservado MB", "Usado MB"],
            tablefmt="grid"
        ))

        # ---------------- RESUMO ----------------
        print("\nResumo Geral")
        print("-" * 70)
        print(f"Tabelas monitoradas : {summary.total_tables}")
        print(f"Total de linhas     : {summary.total_rows:,}")
        print(f"Espaço das tabelas  : {summary.total_space_mb:.2f} MB")
        print(f"Espaço utilizado    : {summary.used_space_mb:.2f} MB")
        print(f"Tamanho do log      : {summary.total_log_size_mb:.2f} MB")
        print(f"Log utilizado       : {summary.total_log_used_mb:.2f} MB")

    except Exception as e:
        print(f"\nErro: {e}")

    finally:
        connection.disconnect()

if __name__ == "__main__":
    main()