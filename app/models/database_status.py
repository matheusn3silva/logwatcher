from dataclasses import dataclass

@dataclass
class DatabaseStatus:
    database_name: str
    recovery_model: str
    log_reuse_wait: str

    @property
    def log_reuse_message(self) -> str:
        messages = {
            "NOTHING": "Log pronto para reutilização",
            "ACTIVE_TRANSACTION": "Existe uma transação ativa impedindo a reutilização do log",
            "LOG_BACKUP": "É necessário realizar um backup do log",
            "REPLICATION": "A replicação está impedindo a reutilização do log",
            "DATABASE_MIRRORING": "O espelhamento está impedindo a reutilização do log",
            "CHECKPOINT": "Aguardando checkpoint."
        }

        return messages.get(
            self.log_reuse_wait,
            "Motivo não mapeado."
        )