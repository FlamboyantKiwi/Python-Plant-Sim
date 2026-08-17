from __future__ import annotations
from src.settings import DEBUG_TEXT

class Log:
    COLORS = {
        "INFO": "\u001b[97m",     # Bright White
        "SUCCESS": "\u001b[92m",  # Bright Green
        "ERROR": "\u001b[91m",    # Bright Red
        "TO_DO": "\u001b[94m",     # Bright Blue
        "WHISPER": "\u001b[90m",  # Bright Black / Dark Grey (For muted or debug logs)
        "RESET": "\u001b[0m"      # Reset Terminal Style
    }

    @staticmethod
    def _print(color_key: str, message: str, label: str | None = None) -> None:
        """Internal helper to check DEBUG_TEXT and handle formatting once."""
        if not DEBUG_TEXT:
            return
        color = Log.COLORS.get(color_key, Log.COLORS["INFO"])
        label = color_key.replace("_", " ").title()
        print(f"{color}[{label}] {message} {Log.COLORS['RESET']}")
    @staticmethod
    def info(message: str) -> None:
        """Prints a general informational message."""
        Log._print("INFO", message)

    @staticmethod
    def success(message: str) -> None:
        """Prints a success message."""
        Log._print("SUCCESS", message)

    @staticmethod
    def error(message: str) -> None:
        """Prints an error or warning message."""
        Log._print("ERROR", message)

    @staticmethod
    def todo(message: str) -> None:
        """Prints a distinct cyan-toned reminder for upcoming features or tasks."""
        Log._print("TO_DO", message)

    @staticmethod
    def whisper(message: str) -> None:
        """Prints a muted grey message for subtle diagnostics or background events."""
        Log._print("WHISPER", message)

    @staticmethod
    def line(length: int = 40) -> None:
        """Prints a solid equals-sign divider line (=====)."""
        Log._print("INFO", "=" * length)

    @staticmethod
    def divider(length: int = 30, char = "-") -> None:
        """Prints a customizable dash or symbol divider line."""
        if not DEBUG_TEXT:
            return
        print(f"{Log.COLORS['INFO']} {char * length} {Log.COLORS['RESET']}")