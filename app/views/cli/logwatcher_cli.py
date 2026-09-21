import os

from tabulate import tabulate

from app.config.database_config import DatabaseConfig
from app.services.connection_profile_service import ConnectionProfileService
from app.services.connection_service import ConnectionService
from app.services.logwatcher_service import LogWatcherService
from app.services.table_parser import TableParser
from app.views.cli import ui
import questionary

class LogWatcherCLI:

    LINE = 60

    def __init__(self):
        self.profile_service = ConnectionProfileService()
        self.connection_service = None
        self.logwatcher_service = None
        self.selected_profile = None
        self.summary = None

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def clear_screen():
        os.system(
            "cls" if os.name == "nt" else "clear"
        )

    @classmethod
    def print_header(cls, title: str):
        cls.clear_screen()
        ui.title(title)

    @classmethod
    def print_error(cls, message: str):
        ui.error(message)

    @classmethod
    def print_success(cls, message: str):
        ui.success(message)

    @staticmethod
    def pause():
        ui.pause()

    @staticmethod
    def ask_confirmation(message: str) -> bool:
        ui.warning(message)
        return ui.confirm("Confirmar a operação?", default=False)

    @staticmethod
    def build_config(
        server: str,
        database: str,
        username: str,
        password: str,
    ) -> DatabaseConfig:

        return DatabaseConfig(
            server=server,
            database=database,
            username=username,
            password=password,
        )

    @staticmethod
    def _parse_tables(tables_text: str):

        if not tables_text:
            return []

        return list(
            dict.fromkeys(
                table.strip()
                for table in tables_text.split(",")
                if table.strip()
            )
        )

    @staticmethod
    def _show_invalid_tables(invalid_tables):

        print("\nTabelas não encontradas:")

        for table in invalid_tables:
            print(f"- {table}")

    # ==========================================================
    # EXECUÇÃO
    # ==========================================================

    def run(self):

        try:

            while True:
                profile = self.profile_menu()

                if profile is None:
                    return

                self.selected_profile = profile

                if not self.connect_to_database():
                    continue

                try:
                    self.main_menu()
                finally:
                    self.disconnect()

        except KeyboardInterrupt:
            print("\n\nAplicação encerrada.")

            self.disconnect()

    # ==========================================================
    # PERFIS
    # ==========================================================

    def profile_menu(self):
        while True:
            profiles = self.profile_service.load_profiles()

            self.print_header("LogWatcher — Perfis de Conexão")

            choices = [
                ui.Choice(
                    title=f"{p.name}  ({p.server} / {p.database})",
                    value=("connect", p),
                )
                for p in profiles
            ]

            if choices:
                choices.append(questionary.Separator("─" * 40))
            else:
                ui.warning("Nenhum perfil de conexão cadastrado.")

            choices += [
                ui.Choice("＋ Novo perfil",    value=("new", None)),
                ui.Choice("✎ Editar perfil",   value=("edit", None)),
                ui.Choice("🗑 Remover perfil",  value=("delete", None)),
                ui.Choice("⏻ Sair",            value=("exit", None)),
            ]

            answer = ui.select("Selecione um perfil ou uma ação:", choices)

            if answer is None:
                return None

            action, profile = answer

            if action == "connect":
                return profile
            if action == "new":
                self.create_profile()
            elif action == "edit":
                self.edit_profile(profiles)
            elif action == "delete":
                self.delete_profile(profiles)
            elif action == "exit":
                return None

    # ==========================================================
    # CRIAÇÃO DE PERFIL
    # ==========================================================

    def create_profile(self):
        self.print_header("Novo perfil de conexão")

        name = input("Nome do perfil: ").strip()
        server = input("IP/Nome do servidor: ").strip()
        database = input("Nome do banco: ").strip()
        username = input("Usuário do banco: ").strip()
        password = ui.password("Senha do banco:")

        tables_text = input(
            "\nTabelas monitoradas "
            "(separadas por vírgula): "
        ).strip()

        if not name:
            self.print_error("O nome do perfil é obrigatório.")

            self.pause()
            return

        if not server:
            self.print_error("O servidor é obrigatório." )

            self.pause()
            return

        if not database:
            self.print_error("O banco de dados é obrigatório.")

            self.pause()
            return

        if not username:
            self.print_error("O usuário é obrigatório.")

            self.pause()
            return

        try:
            tables = TableParser.parse(tables_text)
        except ValueError as error:
            self.print_error(
                f"{error}\n"
                "Verifique se os nomes estão separados por vírgula (,) "
                "e contêm apenas letras, números e underline (_)."
            )
            self.pause()
            return

        if not tables:
            self.print_error("Informe pelo menos uma tabela.")
            self.pause()
            return

        connection_service = ConnectionService()

        try:
            config = self.build_config(
                server,
                database,
                username,
                password,
            )

            print("\nValidando conexão...")

            connection_service.connect(config, profile_name=name)

            logwatcher_service = LogWatcherService(connection_service.repository)

            print("Validando tabelas...")

            valid_tables, invalid_tables = (
                logwatcher_service.validate_tables(
                    ",".join(tables)
                )
            )

            if invalid_tables:
                self._show_invalid_tables(invalid_tables)

            if not valid_tables:
                self.print_error(
                    "Nenhuma das tabelas "
                    "informadas é válida."
                )

                self.pause()
                return

            self.profile_service.create_profile(
                name=name,
                server=server,
                database=database,
                username=username,
                tables=valid_tables,
                invalid_tables=invalid_tables,
            )

            self.print_success(
                "Perfil de conexão criado com sucesso."
            )

            print("\nTabelas monitoradas:")
            for table in valid_tables:
                print(f"  • {table}")

            self.pause()

        except Exception as error:
            self.print_error(
                f"Não foi possível criar o perfil.\n"
                f"Motivo: {error}"
            )

            self.pause()

        finally:
            connection_service.disconnect()

    # ==========================================================
    # EDIÇÃO DE PERFIL
    # ==========================================================

    def edit_profile(self, profiles):
        if not profiles:
            self.print_error("Nenhum perfil de conexão cadastrado.")

            self.pause()
            return

        self.print_header("Editar perfil de conexão")

        profile = ui.select(
            "Selecione o perfil a editar:",
            [ui.Choice(p.name, value=p) for p in profiles]
            + [questionary.Separator("─" * 40), ui.Choice("← Voltar", value=None)],
        )

        if profile is None:
            return

        print(
            f"\nPerfil selecionado: "
            f"{profile.name}"
        )

        print(
            "\nDeixe o campo vazio para "
            "manter o valor atual."
        )

        name = input(f"Nome [{profile.name}]: ").strip()

        server = input(f"Servidor [{profile.server}]: ").strip()

        database = input(f"Banco [{profile.database}]: ").strip()

        username = input(f"Usuário [{profile.username}]: ").strip()

        name = name or profile.name
        server = server or profile.server
        database = database or profile.database
        username = username or profile.username

        print("\nTabelas atualmente cadastradas:")

        if profile.tables:
            for table in profile.tables:
                print(f"- {table}")
        else:
            print("- Nenhuma")

        print(
            "\nInforme somente as NOVAS tabelas "
            "que deseja adicionar."
        )

        tables_text = input(
            "Novas tabelas "
            "(separadas por vírgula): "
        ).strip()

        try:
            new_tables = TableParser.parse(tables_text)
        except ValueError as error:
            self.print_error(
                f"{error}\n"
                "Verifique se os nomes estão separados por vírgula (,) "
                "e contêm apenas letras, números e underline (_)."
            )
            self.pause()
            return
        
        if not new_tables:
            self.print_error(
                "Nenhuma tabela nova informada. "
                "Cancelando a edição — nada foi alterado."
            )
            self.pause()
            return

        password = ui.password(f"Senha para {username}:")

        connection_service = ConnectionService()

        try:
            config = self.build_config(
                server,
                database,
                username,
                password,
            )
            print("\nValidando conexão...")

            connection_service.connect(config, profile_name=name)

            logwatcher_service = LogWatcherService(connection_service.repository)

            print("Validando novas tabelas...")

            valid_new_tables, invalid_tables = (
                logwatcher_service.validate_tables(",".join(new_tables))
            )

            if invalid_tables:
                self._show_invalid_tables(invalid_tables)

            if not valid_new_tables:
                self.print_error(
                    "Nenhuma das novas tabelas "
                    "é válida."
                )

                print(
                    "\nAs tabelas existentes "
                    "não foram alteradas."
                )

                self.pause()
                return

            self._save_profile_changes(
                profile=profile,
                name=name,
                server=server,
                database=database,
                username=username,
                tables=valid_new_tables,
                invalid_tables=invalid_tables,
            )

        except Exception as error:
            self.print_error(
                f"Não foi possível atualizar "
                f"o perfil.\n"
                f"Motivo: {error}"
            )

            self.pause()

        finally:
            connection_service.disconnect()

    def _save_profile_changes(
        self,
        profile,
        name,
        server,
        database,
        username,
        tables,
        invalid_tables=None,
    ):
        try:
            self.profile_service.update_profile(
                profile_id=profile.id,
                name=name,
                server=server,
                database=database,
                username=username,
                tables=tables,
                invalid_tables=invalid_tables,
            )

            self.print_success("Perfil de conexão atualizado.")

            if tables:
                print("\nTabelas novas adicionadas:")

                for table in tables:
                    print(f"- {table}")

            else:
                print(
                    "\nNenhuma nova tabela "
                    "foi adicionada."
                )

            if invalid_tables:
                print("\nTabelas não encontradas (não foram salvas):")

                for table in invalid_tables:
                    print(f"- {table}")

            self.pause()

        except Exception as error:
            self.print_error(
                f"Não foi possível salvar "
                f"o perfil.\n"
                f"Motivo: {error}"
            )

            self.pause()

    # ==========================================================
    # EXCLUSÃO DE PERFIL
    # ==========================================================

    def delete_profile(self, profiles):
        if not profiles:
            self.print_error("Nenhum perfil de conexão cadastrado.")

            self.pause()
            return

        self.print_header("Remover perfil de conexão")

        profile = ui.select(
            "Selecione o perfil a remover:",
            [ui.Choice(p.name, value=p) for p in profiles]
            + [questionary.Separator("─" * 40), ui.Choice("← Voltar", value=None)],
        )

        if profile is None:
            return

        if not self.ask_confirmation(
            f"Remover o perfil "
            f"'{profile.name}'?"
        ):
            print("\nOperação cancelada.")

            self.pause()
            return

        try:
            self.profile_service.delete_profile(profile.id)

            self.print_success("Perfil de conexão removido.")

        except Exception as error:
            self.print_error(
                f"Não foi possível remover "
                f"o perfil.\n"
                f"Motivo: {error}"
            )

        self.pause()

    # ==========================================================
    # CONEXÃO
    # ==========================================================

    def connect_to_database(self):
        self.print_header("Conectando ao banco de dados")

        password = ui.password(f"Senha para {self.selected_profile.username}:")

        config = self.build_config(
            server=self.selected_profile.server,
            database=self.selected_profile.database,
            username=self.selected_profile.username,
            password=password,
        )

        self.connection_service = (
            ConnectionService()
        )

        try:
            print("\nConectando...")

            version = (self.connection_service.connect(config, profile_name=self.selected_profile.name))

            self.logwatcher_service = (
                LogWatcherService(
                    self.connection_service.repository,
                    profile_name=self.selected_profile.name,
                )
            )

            self.print_success(
                "Conexão estabelecida "
                "com sucesso."
            )

            if version:
                print(f"\n{version}")

            self.pause()

            return True

        except Exception as error:
            self.print_error(
                f"Não foi possível conectar "
                f"ao banco.\n"
                f"Motivo: {error}"
            )

            self.pause()

            self.disconnect()

            return False

    def disconnect(self):
        if self.connection_service:
            try:
                self.connection_service.disconnect()
            except Exception:
                pass

        self.connection_service = None
        self.logwatcher_service = None
        self.summary = None

    def _ensure_connection(self):
        if (
            self.connection_service is None
            or self.logwatcher_service is None
        ):

            self.print_error(
                "Não existe uma conexão "
                "ativa com o banco."
            )

            self.pause()

            return False

        return True

    # ==========================================================
    # MENU PRINCIPAL
    # ==========================================================

    def main_menu(self):
        while True:
            self.print_header("LogWatcher")

            questionary.print(
                f"Perfil: {self.selected_profile.name}   "
                f"Banco: {self.selected_profile.database}",
                style="fg:#6e7681",
            )

            option = ui.select("O que deseja fazer?", [
                ui.Choice("📊 Consultar Dashboard",          value="dashboard"),
                ui.Choice("🧹 Limpar Tabela",                value="clean"),
                ui.Choice("💾 Shrink do arquivo de Log",     value="shrink_log"),
                ui.Choice("🗄 Shrink do arquivo de Dados",   value="shrink_data"),
                questionary.Separator("─" * 40),
                ui.Choice("⏏ Desconectar",                  value="exit"),
            ])

            if option in (None, "exit"):
                return
            if option == "dashboard":
                self.show_dashboard()
            elif option == "clean":
                self.clean_table()
            elif option == "shrink_log":
                self.shrink_log()
            elif option == "shrink_data":
                self.shrink_data()

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def show_dashboard(self):
        if not self._ensure_connection():
            return

        if not self.selected_profile.tables:
            self.print_error(
                "Nenhuma tabela de monitoramento "
                "está configurada neste perfil."
            )

            self.pause()
            return

        try:
            self.print_header("Dashboard")

            if self._load_summary() is None:
                return

            self._print_dashboard()

        except Exception as error:
            self.print_error(
                f"Não foi possível consultar "
                f"o Dashboard.\n"
                f"Motivo: {error}"
            )

            self.pause()

    def _print_dashboard(self):
        print("\nArquivos de Log")
        print("-" * 70)

        log_data = [
            [
                log.logical_name,
                f"{log.size_mb:.2f}",
                f"{log.used_mb:.2f}",
                f"{log.free_mb:.2f}",
            ]
            for log in self.summary.logs
        ]

        if log_data:
            print(
                tabulate(
                    log_data,
                    headers=[
                        "Arquivo",
                        "Tamanho MB",
                        "Usado MB",
                        "Livre MB",
                    ],
                    tablefmt="grid",
                )
            )
        else:
            print("Nenhum arquivo de log encontrado.")

        print("\nArquivos de Dados (MDF/NDF)")
        print("-" * 70)

        data_file_data = [
            [
                data_file.logical_name,
                f"{data_file.size_mb:.2f}",
                f"{data_file.used_mb:.2f}",
                f"{data_file.free_mb:.2f}",
            ]
            for data_file in self.summary.data_files
        ]

        if data_file_data:
            print(
                tabulate(
                    data_file_data,
                    headers=[
                        "Arquivo",
                        "Tamanho MB",
                        "Usado MB",
                        "Livre MB",
                    ],
                    tablefmt="grid",
                )
            )
        else:
            print("Nenhum arquivo de dados encontrado.")

        print("\nResumo Geral")
        print("-" * 70)

        print(
            f"Tabelas monitoradas : "
            f"{self.summary.total_tables}"
        )

        print(
            f"Total de linhas     : "
            f"{self.summary.total_rows:,}"
        )

        print(
            f"Espaço das tabelas  : "
            f"{self.summary.total_space_mb:.2f} MB"
        )

        print(
            f"Espaço utilizado    : "
            f"{self.summary.used_space_mb:.2f} MB"
        )

        print(
            f"Tamanho do log      : "
            f"{self.summary.total_log_size_mb:.2f} MB"
        )

        print(
            f"Log utilizado       : "
            f"{self.summary.total_log_used_mb:.2f} MB"
        )       
        
        print(                                   
            f"Tamanho do MDF      : "             
            f"{self.summary.total_data_size_mb:.2f} MB" 
        )                                         

        print(                                   
            f"MDF utilizado       : "             
            f"{self.summary.total_data_used_mb:.2f} MB"  
        )

        self.pause()

    # ==========================================================
    # LIMPEZA
    # ==========================================================

    def clean_table(self):
        if not self._ensure_connection():
            return

        if self.summary is None:
            if self._load_summary() is None:
                return

        if not self.summary.tables:
            self.print_error(
                "Nenhuma tabela monitorada "
                "foi encontrada."
            )

            self.pause()
            return

        action = None

        try:
            self.print_header("Limpeza de Tabela")

            table = ui.select(
                "Selecione a tabela:",
                [
                    ui.Choice(
                        f"{t.schema.upper()}.{t.name.upper()}  "
                        f"({t.rows} linhas / {t.total_mb:.2f} MB)",
                        value=t,
                    )
                    for t in self.summary.tables
                ] + [
                    questionary.Separator("─" * 40),
                    ui.Choice("← Voltar", value=None),
                ],
            )

            if table is None:
                return

            index = self.summary.tables.index(table)

            action = ui.select(
                "Modo de limpeza:",
                [
                    ui.Choice(
                        "TRUNCATE — remove todos os registros (rápido, ignora FKs)",
                        value="TRUNCATE",
                    ),
                    ui.Choice(
                        "DELETE   — remove respeitando FKs (mais lento, gera log)",
                        value="DELETE",
                    ),
                    questionary.Separator("─" * 40),
                    ui.Choice("← Voltar", value=None),
                ],
            )

            if action is None:
                return

            table_name = (
                f"{table.schema.upper()}."
                f"{table.name.upper()}"
            )

            print("\nATENÇÃO")
            print(
                f"Tabela   : {table_name}"
            )
            print(
                f"Operação : {action}"
            )

            print(
                "Esta operação poderá remover "
                "todos os registros da tabela."
            )

            if not self.ask_confirmation(
                "Deseja realmente executar "
                "esta operação?"
            ):
                print("\nOperação cancelada.")
                self.pause()
                return

            if action == "TRUNCATE":
                self.logwatcher_service.truncate_monitored_table(self.summary, index)
            else:
                self.logwatcher_service.delete_monitored_table(self.summary, index)

            self.print_success(f"{action} executado com sucesso.")
            self._load_summary()

        except Exception as error:
            self.print_error(
                f"Não foi possível executar "
                f"{action or 'a operação'}.\n"
                f"Motivo: {error}"
            )

        self.pause()

    # ==========================================================
    # SHRINK
    # ==========================================================

    def shrink_log(self):
        if not self._ensure_connection():
            return

        try:
            status, logs = (self.logwatcher_service.get_log_status())

            self.print_header("Shrink do arquivo de Log")

            print(
                f"Banco            : "
                f"{status.database_name}"
            )

            print(
                f"Recovery Model   : "
                f"{status.recovery_model}"
            )

            print(
                f"Reutilização Log : "
                f"{status.log_reuse_wait}"
            )

            print(
                f"Explicação       : "
                f"{status.log_reuse_message}"
            )

            print("\nArquivos de Log (LDF)")
            print("-" * self.LINE)

            if not logs:
                self.print_error(
                    "Nenhum arquivo de log "
                    "foi encontrado."
                )
                self.pause()
                return

            log = ui.select(
                "Selecione o arquivo de log:",
                [
                    ui.Choice(
                        f"{l.logical_name}  "
                        f"(Reservado: {l.size_mb:.2f} MB / Livre: {l.free_mb:.2f} MB)",
                        value=l,
                    )
                    for l in logs
                ] + [questionary.Separator("─" * 40), ui.Choice("← Voltar", value=None)],
            )

            if log is None:
                return

            index = logs.index(log)

            print("\nATENÇÃO")

            print(
                "O SQL Server determinará "
                "o menor tamanho possível."
            )

            print(
                "Transações ativas podem impedir "
                "a redução do arquivo."
            )

            if not self.ask_confirmation(
                f"Executar SHRINK no arquivo "
                f"'{log.logical_name}'?"
            ):
                print("\nOperação cancelada.")

                self.pause()
                return

            before = log.size_mb

            self.logwatcher_service.shrink_log(index)

            _, updated_logs = (self.logwatcher_service.get_log_status())

            if index >= len(updated_logs):
                raise RuntimeError(
                    "O arquivo de log não foi "
                    "encontrado após a operação."
                )

            after = updated_logs[index].size_mb

            self.print_header("Resultado do SHRINK")

            print("Operação de SHRINK concluída.")

            print("-" * self.LINE)

            print(
                f"Arquivo    : "
                f"{log.logical_name}"
            )

            print(
                f"Antes      : "
                f"{before:.2f} MB"
            )

            print(
                f"Depois     : "
                f"{after:.2f} MB"
            )

            print(
                f"Recuperado : "
                f"{before - after:.2f} MB"
            )

            if after >= before:
                print(
                    "\nO SHRINK foi executado, "
                    "porém não houve redução "
                    "no tamanho físico "
                    "do arquivo."
                )

        except Exception as error:
            self.print_error(
                f"Não foi possível executar "
                f"o SHRINK.\n"
                f"Motivo: {error}"
            )

        self.pause()

    def shrink_data(self):
        if not self._ensure_connection():
            return

        try:
            status, data_files = (self.logwatcher_service.get_data_status())

            self.print_header("Shrink do arquivo de Dados")

            print(
                f"Banco            : "
                f"{status.database_name}"
            )

            print(
                f"Recovery Model   : "
                f"{status.recovery_model}"
            )

            print("\nArquivos de Dados")
            print("-" * self.LINE)

            for index, data_file in enumerate(
                data_files,
                start=1
            ):
                print(
                    f"{index} - "
                    f"{data_file.logical_name} | "
                    f"Reservado: "
                    f"{data_file.size_mb:.2f} MB | "
                    f"Usado: "
                    f"{data_file.used_mb:.2f} MB | "
                    f"Livre: "
                    f"{data_file.free_mb:.2f} MB"
                )

            if not data_files:
                self.print_error(
                    "Nenhum arquivo de dados "
                    "foi encontrado."
                )
                self.pause()
                return

            data_file = ui.select(
                "Selecione o arquivo de dados:",
                [
                    ui.Choice(
                        f"{d.logical_name}  "
                        f"(Reservado: {d.size_mb:.2f} MB / Livre: {d.free_mb:.2f} MB)",
                        value=d,
                    )
                    for d in data_files
                ] + [questionary.Separator("─" * 40), ui.Choice("← Voltar", value=None)],
            )

            if data_file is None:
                return

            index = data_files.index(data_file)

            print("\nATENÇÃO")

            print(
                "O SQL Server determinará "
                "o menor tamanho possível."
            )

            print(
                "Reduzir o arquivo de dados pode "
                "gerar fragmentação de índices."
            )

            if not self.ask_confirmation(
                f"Executar SHRINK no arquivo "
                f"'{data_file.logical_name}'?"
            ):

                print("\nOperação cancelada.")
                self.pause()
                return

            before = data_file.size_mb

            self.logwatcher_service.shrink_data(index)

            _, updated_files = (
                self.logwatcher_service.get_data_status()
            )

            if index >= len(updated_files):

                raise RuntimeError(
                    "O arquivo de dados não foi "
                    "encontrado após a operação."
                )

            after = updated_files[index].size_mb

            self.print_header("Resultado do SHRINK")

            print("Operação de SHRINK concluída.")

            print("-" * self.LINE)

            print(
                f"Arquivo    : "
                f"{data_file.logical_name}"
            )

            print(
                f"Antes      : "
                f"{before:.2f} MB"
            )

            print(
                f"Depois     : "
                f"{after:.2f} MB"
            )

            print(
                f"Recuperado : "
                f"{before - after:.2f} MB"
            )

            if after >= before:
                print(
                    "\nO SHRINK foi executado, "
                    "porém não houve redução "
                    "no tamanho físico "
                    "do arquivo."
                )

        except Exception as error:
            self.print_error(
                f"Não foi possível executar "
                f"o SHRINK.\n"
                f"Motivo: {error}"
            )

        self.pause()

    # ==========================================================
    # AUXILIARES
    # ==========================================================

    def _load_summary(self):
        try:
            tables_text = ",".join(self.selected_profile.tables)

            self.summary = (
                self.logwatcher_service.analyze_database(
                    tables_text
                )
            )

            return self.summary

        except Exception as error:
            self.summary = None

            self.print_error(
                f"Não foi possível atualizar "
                f"os dados.\n"
                f"Motivo: {error}"
            )

            self.pause()

            return None