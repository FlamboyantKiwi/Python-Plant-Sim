from __future__ import annotations

COLORS = {
        "INFO": "\u001b[97m",     # Bright White
        "SUCCESS": "\u001b[92m",  # Bright Green
        "ERROR": "\u001b[91m",    # Bright Red
        "TO_DO": "\u001b[94m",     # Bright Blue
        "WHISPER": "\u001b[90m",  # Bright Black / Dark Grey (For muted or debug logs)
        "RESET": "\u001b[0m"      # Reset Terminal Style
    }

class Log: 
    _debug_enabled: bool | None = None
    @classmethod
    def _is_debug(cls) -> bool:
        """Imports and caches the debug text setting."""
        if cls._debug_enabled is None:
            from src.config.settings import DEBUG_TEXT
            cls._debug_enabled = DEBUG_TEXT
        return cls._debug_enabled
    
    @staticmethod
    def _print(color_key: str, message: str, label: str | None = None) -> None:
        """Internal helper to check DEBUG_TEXT and handle formatting once."""
        if not Log._is_debug():
            return
        color = COLORS.get(color_key, COLORS["INFO"])
        label = color_key.replace("_", " ").title()
        print(f"{color}[{label}] {message} {COLORS['RESET']}")
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
        if not Log._is_debug():
            return
        print(f"{COLORS['INFO']} {char * length} {COLORS['RESET']}")