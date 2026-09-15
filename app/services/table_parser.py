import re

class TableParser:
    @staticmethod
    def parse(text: str) -> list[str]:
        tables = []

        for table in text.split(','):
            table = table.strip()

            if not table:
                continue

            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table):
                raise ValueError(
                    f"Nome da tabela inválido ou inexistente: {table}"
                )

            tables.append(table)

        return tables