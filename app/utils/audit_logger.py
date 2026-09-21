import getpass
from datetime import datetime
from pathlib import Path

import os, sys

if getattr(sys, "frozen", False):
    LOG_DIR = Path(os.getenv("APPDATA")) / "LogWatcher" / "logs"
else:
    LOG_DIR = Path(__file__).resolve().parents[2] / "logs"


class AuditLogger:
    @staticmethod
    def _windows_user() -> str:
        try:
            return getpass.getuser()
        except Exception:
            return "desconhecido"

    @staticmethod
    def _log_file() -> Path:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        return LOG_DIR / f"logwatcher_audit_{today}.log"

    @staticmethod
    def log(
        database: str,
        username: str,
        message: str,
        profile: str = "-",
        action: str = "-",
        status: str = "SUCESSO",
    ) -> None:
        log_file = AuditLogger._log_file()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        windows_user = AuditLogger._windows_user()

        line = (
            f"[{timestamp}] [{status}] "
            f"Perfil={profile} | Banco={database} | "
            f"Usuário SQL={username} | Usuário Windows={windows_user} | "
            f"Ação={action} | Detalhe={message}\n"
        )

        with log_file.open("a", encoding="utf-8") as file:
            file.write(line)