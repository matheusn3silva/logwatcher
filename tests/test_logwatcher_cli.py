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

        summary = service.analyze_tables(tables_text)

        print(f"\nTabelas encontradas: {summary.total_tables}")
        print(f"Total de linhas: {summary.total_rows:,}")
        print(f"Espaço total: {summary.total_space_mb:.2f} MB")
        print(f"Espaço utilizado: {summary.used_space_mb:.2f} MB")
        
        data = []

        for table in summary.tables:

            data.append([
                f"{table.name}",
                f"{table.rows:,}", 
                f"{table.total_mb:.2f}", 
                f"{table.used_mb:.2f}"
            ])

        table = tabulate(
            data,
            headers=["Tabela", "Linhas", "Total MB", "Usado MB"],
            tablefmt="grid"
        )

        print(table)

    except Exception as e:
        print(f"\nErro: {e}")

    finally:
        connection.disconnect()

if __name__ == "__main__":
    main()