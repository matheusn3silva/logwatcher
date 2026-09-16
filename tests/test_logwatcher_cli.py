from app.services.connection_service import ConnectionService
from app.config.database_config import DatabaseConfig
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

    connection_service = ConnectionService()

    summary = None

    try:
        print("\nConectando...")

        version = connection_service.connect(config)
        print("Conectado com sucesso!")
        print(f"SQL Server: {version.splitlines()[0]}")

        service = LogWatcherService(connection_service.repository)

        while True:
            print("\n=== MENU ===")
            print("1 - Consultar Dashboard")
            print("2 - Limpar Tabela")
            print("3 - Shrink do arquivo de Log")
            print("0 - Sair")

            option = input("\nEscolha: ")

            if option == "1":
                tables_text = input(
                    "\nDigite as tabelas separadas por vírgula: "
                )

                if tables_text == "":
                    print("\nERRO: A lista de tabelas não pode ser vazio.")
                    continue
                
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
            elif option == "2":

                if summary is None:
                    print("\nFaça uma consulta primeiro.")
                    continue

                print("\nTabelas Monitoradas")

                for i, table in enumerate(summary.tables, start=1):
                    print(f"{i} - {table.schema.upper()}.{table.name.upper()}")

                choice_text = input("\nEscolha: ")

                if not choice_text.isdigit():
                    print("\nEscolha inválida.")
                    continue

                choice = int(choice_text) - 1
                
                if choice < 0 or choice >= len(summary.tables):
                    print("\nTabela inválida.")
                    continue
                
                print("\nModo de limpeza")
                print("1 - TRUNCATE (mais rápido)")
                print("2 - DELETE (mais seguro para FK)")

                mode = input("\nEscolha: ")
                
                if mode not in ("1", "2"):
                    print("\nModo inválido.")
                    continue
                
                action = "TRUNCATE" if mode == "1" else "DELETE"

                confirm = input(f"\nDigite SIM para executar em {table.schema.upper()}.{table.name.upper()}: ")

                if confirm.upper() != "SIM":
                    print("\nOperação cancelada.")
                    continue

                try:
                    if mode == "1":
                        service.truncate_monitored_table(summary, choice)
                    else:
                        service.delete_monitored_table(summary, choice)
                        
                    print(f"\n{action} executado com sucesso!")
                    summary = service.analyze_database(",".join(table.name for table in summary.tables))
                except Exception as e:
                    print(f"\nNão foi possível executar o {action}.")
                    print(f"Motivo: {e}")

            elif option == "3":

                status, logs = service.get_log_status()

                print("\n" + "=" * 50)
                print("STATUS DO LOG")
                print("=" * 50)

                print(f"Banco            : {status.database_name}")
                print(f"Recovery Model   : {status.recovery_model}")
                print(f"Reutilização Log : {status.log_reuse_wait}")
                print(f"Explicação       : {status.log_reuse_message}")

                print("\nArquivos de Log")

                for i, log in enumerate(logs, start=1):
                    print(
                        f"{i} - {log.logical_name}"
                        f" | Reservado: {log.size_mb:.2f} MB"
                        f" | Usado: {log.used_mb:.2f} MB"
                        f" | Livre: {log.free_mb:.2f} MB"
                    )

                choice_text = input("\nEscolha: ")
                
                if not choice_text.isdigit():
                    print("\nEscolha inválida.")
                    continue
                
                choice = int(choice_text) - 1
                
                if choice < 0 or choice >= len(logs):
                    print("\nArquivo inválido.")
                    continue

                print("\nAviso:")
                print("- O LogWatcher tentará reduzir o arquivo automaticamente.")
                print("- O SQL Server decidirá o menor tamanho possível.")
                print("- O usuário precisa possuir privilégios de db_owner ou sysadmin.")
                print("- Caso existam transações ativas, o tamanho pode não diminuir.")

                confirm = input("\nDigite SIM para confirmar: ")

                if confirm.upper() != "SIM":
                    print("\nOperação cancelada.")
                    continue

                before = logs[choice].size_mb

                service.shrink_log(choice)

                _, logs = service.get_log_status()

                after = logs[choice].size_mb
                
                print("\nSHRINK realizado com sucesso! \n\nResultado:")
                print("-" * 40)
                print(f"Antes      : {before:.2f} MB")
                print(f"Depois     : {after:.2f} MB")
                print(f"Recuperado : {before - after:.2f} MB")

            elif option == "0":
                break

            else:
                print("Opção inválida.")


    except Exception as e:
        print(f"\nErro: {e}")

    finally:
        connection_service.disconnect()

if __name__ == "__main__":
    main()