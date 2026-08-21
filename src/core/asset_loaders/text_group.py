from __future__ import annotations
from ..types import TextConfig
from .config_group import ConfigGroup

class TextGroup(ConfigGroup):
    """Manages TextConfig styles (presets like 'TITLE', 'HUD')."""
    def load(self) -> None:
        self.storage.update(self.raw_data)
        self.default = self.storage.get("default", TextConfig())

    def get_config(self, key: str) -> TextConfig:
        return self.get_val(key)