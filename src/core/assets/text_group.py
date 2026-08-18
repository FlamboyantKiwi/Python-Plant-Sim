from __future__ import annotations
from src.core.types import TextConfig
from src.core.assets.asset_data import TEXT
from .config_group import ConfigGroup

class TextGroup(ConfigGroup):
    """Manages TextConfig styles (presets like 'TITLE', 'HUD')."""
    def load(self) -> None:
        self.storage.update(TEXT)
        self.default = self.storage.get("default", TextConfig())

    def get_config(self, key: str) -> TextConfig:
        return self.get_val(key)