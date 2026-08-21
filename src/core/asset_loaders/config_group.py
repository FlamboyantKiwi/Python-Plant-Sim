from __future__ import annotations
import os
import inspect
from typing import Any
from .. import Log
from .asset_group import AssetGroup

class ConfigGroup(AssetGroup):
    """Parent for Dictionary-based assets (Colours, Text). Handles: Storage, Missing Keys, Defaults, and Debugging."""
    def __init__(self, manager: Any, raw_data:Any = None) -> None:
        super().__init__(manager, raw_data=raw_data)
        self.missing = set()
        self.default = None

    def get_val(self, key: Any) -> Any:
        val = self.storage.get(key)
        if val:
            return val
        if key not in self.missing:
            caller_info = "Unknown source"
            try:
                for frame in inspect.stack():
                    filename = os.path.basename(frame.filename)
                    ignore_files = ["asset_loader.py", "ui_elements.py", "helper.py"]
                    if filename not in ignore_files:
                        caller_info = f"{filename}:{frame.lineno}"
                        break
            except Exception:
                pass
            Log.error(f"[{self.__class__.__name__}] Warning: Missing Key '{key}' (Requested by: {caller_info})")
            self.missing.add(key)
        return self.default

    def debug_print(self) -> None:
        super().debug_print()
        if self.missing:
            Log.error(f"MISSING KEYS ({len(self.missing)}):")
            for key in sorted(self.missing):
                Log.info(f"  [X] {key}")
        else:
            Log.success("No missing keys.")
        self.print_line_break()