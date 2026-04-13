from __future__ import annotations
import os
import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

# Runtime Imports
from core.spritesheet import SpriteSheet

# Type-Only Imports
if TYPE_CHECKING:
    from custom_types import Num, EntityType
    from core.assets import AssetLoader

class AssetGroup(ABC):
    """Universal Base Class. 
    Automatically gives every subclass its own unique STORAGE dictionary."""
    
    def __init__(self, manager:AssetLoader) -> None:
        self.manager = manager
        self.storage: dict[Any, Any] = {}

    @abstractmethod
    def load(self) -> None: pass
    
    def debug_print(self) -> None:
        """Base debug header. Subclasses should call super().debug_print() first."""
        print(f"\n--- {self.__class__.__name__} ({len(self.storage)} items loaded) ---")

    def print_line_break(self) -> None:
        print("-" * 30)

    def clean_up(self) -> None: pass

class ConfigGroup(AssetGroup):
    """Parent for Dictionary-based assets (Colours, Text).
    Handles: Storage, Missing Keys, Defaults, and Debugging."""
    
    def __init__(self, manager: AssetLoader) -> None:
        super().__init__(manager)
        self.missing = set()
        self.default = None
        
    def get_val(self, key: Any) -> Any:
        """Generic lookup with error tracking."""
        # 1. Try Exact Match
        val = self.storage.get(key)
        if val: 
            return val

        # 2. Handle Missing & Stack Trace
        if key not in self.missing:
            # --- YOUR DEBUG LOGIC ---
            caller_info = "Unknown source"
            try:
                # Look back through the stack to find who called this
                for frame in inspect.stack():
                    filename = os.path.basename(frame.filename)
                    # Skip these files to find the 'real' culprit
                    ignore_files = ["asset_loader.py", "ui_elements.py", "helper.py"]
                    
                    if filename not in ignore_files:
                        # Format: filename:line_number
                        caller_info = f"{filename}:{frame.lineno}"
                        break
            except Exception:
                pass

            print(f"[{self.__class__.__name__}] Warning: Missing Key '{key}' (Requested by: {caller_info})")            
            self.missing.add(key)
            
        return self.default

    def debug_print(self) -> None:
        super().debug_print()
        # Print Missing
        if self.missing:
            print(f"MISSING KEYS ({len(self.missing)}):")
            for key in sorted(self.missing):
                print(f"  [X] {key}")
        else:
            print("No missing keys.")
        self.print_line_break()

class SpriteGroup(AssetGroup):
    """Parent for Sheet-based assets (Tiles, Tools, Plants)."""
    SCALE_FACTOR:int = 2
    TILE_SIZE:int = 32

    # Accept **sheet_files so the loader can pass any number of named sheets
    def __init__(self, manager: AssetLoader, **sheet_files: str) -> None:
        super().__init__(manager)
        self.sheet_files = sheet_files
        self.loaded_sheets: dict[str, SpriteSheet] = {}

    def get_sheet(self, key: str = "main") -> SpriteSheet | None:
        """Loads and caches a SpriteSheet based on the configuration passed from AssetLoader."""
        # Return cached sheet if it already exists
        if key in self.loaded_sheets:
            return self.loaded_sheets[key]
            
        # Look up the filename in our kwargs dict
        filename = self.sheet_files.get(key)
        if not filename:
            print(f"[FATAL] {self.__class__.__name__} asked for '{key}', but it wasn't provided in AssetLoader!")
            return None
            
        # Safely load and cache the new sheet
        try:
            sheet = SpriteSheet(f"{filename}.png")
            self.loaded_sheets[key] = sheet
            print(f"[{self.__class__.__name__}] Successfully loaded sheet: {filename}.png")
            return sheet
        except Exception as e:
            print(f"Failed to load sheet '{filename}' for {self.__class__.__name__}: {e}")
            return None
        
    def debug_print(self) -> None:
        super().debug_print()
        self.print_line_break()
