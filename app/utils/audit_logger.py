from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "logwatcher_audit.log"


class AuditLogger:
    @staticmethod
    def log(database: str, username: str, message: str) -> None:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d -- %H:%M:%S")

        line = (
            f"{timestamp} -- Banco: {database} -- "
            f"Usuário: {username} -- {message}\n"
        )

        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(line)