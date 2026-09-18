import os
from app.services.connection_service import ConnectionService
from app.config.database_config import DatabaseConfig
from app.services.logwatcher_service import LogWatcherService
from app.services.connection_profile_service import ConnectionProfileService
from tabulate import tabulate

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("=" * 50)
    print("LogWatcher - Teste via Terminal")
    print("=" * 50)

    profile_service = ConnectionProfileService()

    selected_profile = None

    while selected_profile is None:

        profiles = profile_service.load_profiles()

        print("\nPerfis de conexões Salvos")
        print("=" * 50)

        if profiles:
            for i, profile in enumerate(profiles, start=1):
                print(f"{i} - {profile.name}")
        else:
            print("\nCrie seu primeiro perfil de conexão.")

        print("\nN - Novo perfil de conexão")
        print("E - Editar perfil de conexão")
        print("R - Remover perfil de conexão")
        print("S - Sair")

        choice = input("\nEscolha: ").strip().upper()

        if choice.isdigit():

            index = int(choice) - 1

            if 0 <= index < len(profiles):
                selected_profile = profiles[index]
            else:
                print("=" * 50)
                print("ERRO: Perfil de conexão inválido.")
                print("=" * 50)

        elif choice == "N":

            name = input("Nome do perfil de conexão: ")
            server = input("IP do Servidor: ")
            database = input("Nome do Banco: ")
            username = input("Usuário do Banco: ")
            password = input("Senha do Banco: ")

            tables_text = input(
                "\nDigite as tabelas de logs/auditoria (separadas por vírgula): "
            )

            tables = [
                table.strip()
                for table in tables_text.split(",")
                if table.strip()
            ]
            
            connection_service = ConnectionService()

            config = DatabaseConfig(
                server=server,
                database=database,
                username=username,
                password=password
            )

            try:
                connection_service.connect(config)

                service = LogWatcherService(connection_service.repository)

                valid, invalid = service.validate_tables(tables_text)

            except Exception as e:
                clear_screen()
                print("=" * 50)
                print(f"Erro ao conectar ao banco: {e}")
                print("=" * 50)
                continue

            finally:
                connection_service.disconnect()

            profile_service.create_profile(
                name,
                server,
                database,
                username,
                valid
            )

            clear_screen()
            print("=" * 50)
            print("Perfil de conexão criado com sucesso!")
            print("=" * 50)

            if valid:
                print("\nTabelas adicionadas:")
                for table in valid:
                    print(f"- {table}")

            if invalid:
                print("\nAs seguintes tabelas não foram encontradas:")
                for table in invalid:
                    print(f"- {table}")


        elif choice == "E":

            if not profiles:
                clear_screen()
                print("!" * 50)
                print("ERRO: Nenhum perfil de conexão disponível.")
                print("!" * 50)
                continue

            for i, profile in enumerate(profiles, start=1):
                print(f"{i} - {profile.name}")

            index_text = input("\nEscolha: ")

            if not index_text.isdigit():
                clear_screen()
                print("=" * 50)
                print("ERRO: Escolha inválida.")
                print("=" * 50)
                continue

            index = int(index_text) - 1

            if not (0 <= index < len(profiles)):
                clear_screen()
                print("=" * 50)
                print("ERRO: Perfil de conexão inválido.")
                print("=" * 50)
                continue

            profile = profiles[index]

            name = input(f"Nome ({profile.name}): ") or profile.name
            server = input(f"IP do Servidor ({profile.server}): ") or profile.server
            database = input(f"Nome do Banco ({profile.database}): ") or profile.database
            username = input(f"Usuário do Banco ({profile.username}): ") or profile.username

            print("\nTabelas atuais:")
            for table in profile.tables:
                print(f"- {table}")

            tables_text = input(
                "\nDigite novas tabelas (opcional): "
            )
            
            tables = (
                [t.strip() for t in tables_text.split(",") if t.strip()]
                if tables_text
                else profile.tables
            )

            profile_service.update_profile(
                profile.id,
                name,
                server,
                database,
                username,
                tables
            )

            clear_screen()
            print("=" * 50)
            print("SUCESSO: Perfil de conexão atualizado.")
            print("=" * 50)

        elif choice == "R":

            if not profiles:
                clear_screen()
                print("=" * 50)
                print("ERRO: Nenhum perfil de conexão disponível.")
                print("=" * 50)
                continue

            for i, profile in enumerate(profiles, start=1):
                print(f"{i} - {profile.name}")

            index_text = input("\nEscolha: ")

            if not index_text.isdigit():
                clear_screen()
                print("=" * 50)
                print("ERRO: Escolha inválida.")
                print("=" * 50)
                continue

            index = int(index_text) - 1

            if not (0 <= index < len(profiles)):
                clear_screen()
                print("=" * 50)
                print("ERRO: Perfil de conexão inválido ou inexistente.")
                print("=" * 50)
                continue

            confirm = input(
                f"\nDigite SIM para remover {profiles[index].name}: "
            )

            clear_screen()
            if confirm.upper() == "SIM":
                profile_service.delete_profile(
                    profiles[index].id
                )
                print("=" * 50)
                print("SUCESSO: Perfil de conexão removido.")
                print("=" * 50)

        elif choice == "S":
            return

        else:
            print("=" * 50)
            print("ERRO: Opção inválida.")
            print("=" * 50)

    server = selected_profile.server
    database = selected_profile.database
    username = selected_profile.username

    password = input(f"Senha para {username}: ")

    config = DatabaseConfig(
        server=server,
        database=database,
        username=username,
        password=password
    )

    connection_service = ConnectionService()

    summary = None

    try:
        clear_screen()
        print("\nConectando...")

        version = connection_service.connect(config)
        clear_screen()
        print("=" * 50)
        print("Conectado com sucesso!")
        print(f"SQL Server: {version.splitlines()[0]}")
        print("=" * 50)

        service = LogWatcherService(connection_service.repository)

        while True:
            print("\n===== MENU =====")
            print("1 - Consultar Dashboard")
            print("2 - Limpar Tabela")
            print("3 - Shrink do arquivo de Log")
            print("0 - Sair")

            option = input("\nEscolha: ")
            clear_screen()

            if option == "1":

                if not selected_profile.tables:
                    print("=" * 50)
                    print("Este perfil de conexão não possui tabelas configuradas.")
                    print("Edite o perfil de conexão e adicione pelo menos uma tabela.")
                    print("=" * 50)
                    continue
                
                tables_text = ",".join(selected_profile.tables)

                print("\nTabelas monitoradas:")
                print(", ".join(selected_profile.tables))

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
                    print("=" * 50)
                    print("ERRO: Perfil não possui tabelas, edita o perfil de conexão.")
                    print("=" * 50)
                    continue

                print("\nTabelas Monitoradas")

                for i, table in enumerate(summary.tables, start=1):
                    print(f"{i} - {table.schema.upper()}.{table.name.upper()}")

                choice_text = input("\nEscolha: ")

                if not choice_text.isdigit():
                    clear_screen()
                    print("=" * 50)
                    print("ERRO: Escolha inválida.")
                    print("=" * 50)
                    continue

                choice = int(choice_text) - 1
                
                if choice < 0 or choice >= len(summary.tables):
                    clear_screen()
                    print("=" * 50)
                    print("ERRO: Opção inválida.")
                    print("=" * 50)
                    continue

                table = summary.tables[choice]
                
                print("\nModo de limpeza")
                print("1 - TRUNCATE (mais rápido)")
                print("2 - DELETE (mais seguro para FK)")

                mode = input("\nEscolha: ")
                
                if mode not in ("1", "2"):
                    clear_screen()
                    print("=" * 50)
                    print("ERRO: Modo inválido.")
                    print("=" * 50)
                    continue
                
                action = "TRUNCATE" if mode == "1" else "DELETE"

                confirm = input(f"\nDigite SIM para executar em {table.schema.upper()}.{table.name.upper()}: ")

                clear_screen()
                if confirm.upper() != "SIM":
                    print("=" * 50)
                    print("ERRO: Operação cancelada.")
                    print("=" * 50)
                    continue

                try:
                    if mode == "1":
                        service.truncate_monitored_table(summary, choice)
                    else:
                        service.delete_monitored_table(summary, choice)
                        
                    print("=" * 50)
                    print(f"\n{action} executado com sucesso!")
                    print("=" * 50)
                    summary = service.analyze_database(",".join(table.name for table in summary.tables))
                except Exception as e:
                    print("=" * 50)
                    print(f"Não foi possível executar o {action}.")
                    print(f"Motivo: {e}")
                    print("=" * 50)

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
                    clear_screen()
                    print("=" * 50)
                    print("ERRO: Escolha inválida.")
                    print("=" * 50)
                    continue
                
                choice = int(choice_text) - 1
                
                if choice < 0 or choice >= len(logs):
                    clear_screen()
                    print("=" * 50)
                    print("ERRO: Arquivo inválido.")
                    print("=" * 50)
                    continue

                print("\nAviso:")
                print("- O LogWatcher tentará reduzir o arquivo automaticamente.")
                print("- O SQL Server decidirá o menor tamanho possível.")
                print("- O usuário precisa possuir privilégios de db_owner ou sysadmin.")
                print("- Caso existam transações ativas, o tamanho pode não diminuir.")

                confirm = input("\nDigite SIM para confirmar: ")

                clear_screen()
                if confirm.upper() != "SIM":
                    print("=" * 50)
                    print("Operação cancelada.")
                    print("=" * 50)
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
                print("=" * 50)
                print("ERRO: Opção inválida.")
                print("=" * 50)


    except Exception as e:
        print(f"\nErro: {e}")
        print("=" * 50)

    finally:
        connection_service.disconnect()

if __name__ == "__main__":
    main()