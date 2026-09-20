import getpass
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "logwatcher_audit.log"


class AuditLogger:
    @staticmethod
    def _windows_user() -> str:
        try:
            return getpass.getuser()
        except Exception:
            return "desconhecido"

    @staticmethod
    def log(
        database: str,
        username: str,
        message: str,
        profile: str = "-",
        action: str = "-",
        status: str = "SUCESSO",
    ) -> None:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        windows_user = AuditLogger._windows_user()

        line = (
            f"[{timestamp}] [{status}] "
            f"Perfil={profile} | Banco={database} | "
            f"Usuário SQL={username} | Usuário Windows={windows_user} | "
            f"Ação={action} | Detalhe={message}\n"
        )

        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(line)