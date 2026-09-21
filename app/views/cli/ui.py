import questionary
from questionary import Choice, Style

LW_STYLE = Style([
    ("qmark",       "fg:#00b4d8 bold"),
    ("question",    "bold fg:#e6edf3"),
    ("answer",      "fg:#3fb950 bold"),
    ("pointer",     "fg:#00b4d8 bold"),
    ("highlighted", "fg:#00b4d8 bold"),
    ("selected",    "fg:#3fb950"),
    ("separator",   "fg:#6e7681"),
    ("instruction", "fg:#6e7681 italic"),
    ("text",        "fg:#e6edf3"),
    ("disabled",    "fg:#6e7681 italic"),
])


def select(message: str, choices, default=None):
    """Menu com setas. Devolve o `value` da Choice ou None se ESC/Ctrl+C."""
    return questionary.select(
        message,
        choices=choices,
        style=LW_STYLE,
        qmark="›",
        instruction="(use ↑ ↓ e ENTER)",
        default=default,
        use_shortcuts=False,
    ).ask()


def text(message: str, default: str = "") -> str:
    answer = questionary.text(message, default=default, style=LW_STYLE, qmark="›").ask()
    return (answer or "").strip()


def password(message: str) -> str:
    return questionary.password(message, style=LW_STYLE, qmark="›").ask() or ""


def confirm(message: str, default: bool = False) -> bool:
    return bool(questionary.confirm(message, default=default, style=LW_STYLE, qmark="!").ask())


def pause():
    questionary.press_any_key_to_continue(
        "Pressione qualquer tecla para continuar...", style=LW_STYLE
    ).ask()


def title(text_: str):
    questionary.print(f"\n{text_}", style="bold fg:#00b4d8")
    questionary.print("─" * 60, style="fg:#6e7681")


def error(message: str):
    questionary.print(f"\n✖ {message}\n", style="bold fg:#f85149")


def success(message: str):
    questionary.print(f"\n✔ {message}\n", style="bold fg:#3fb950")


def warning(message: str):
    questionary.print(f"\n⚠ {message}\n", style="bold fg:#d29922")