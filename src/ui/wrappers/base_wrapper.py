from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame

if TYPE_CHECKING:
    from src.custom_types import UIElement

class BaseWrapper:
    """Base class for all UI wrappers. Automatically delegates missing attributes to the target."""
    def __init__(self, target: UIElement):
        self.target:Any = target

    def __getattr__(self, attr: str) -> Any:
        # Safety check to prevent infinite recursion if target isn't set yet
        if attr == "target":
            raise AttributeError(f"'{type(self).__name__}' has no target initialized.")
        return getattr(self.target, attr)

    def __setattr__(self, attr: str, value: Any) -> None:
        """Intelligently routes variable assignments to either the Wrapper or the Target."""
        # Allow the wrapper to set its own variables (like 'target', 'interval', 'surf_normal')
        if attr == "target" or attr in self.__dict__:
            super().__setattr__(attr, value)
        # If the target owns the attribute (like 'is_active' or 'is_hovered'), forward it down!
        elif hasattr(self, "target") and hasattr(self.target, attr):
            setattr(self.target, attr, value)
        # Fallback
        else:
            super().__setattr__(attr, value)
    
    def update(self, *args, **kwargs) -> None:
        """Default pass-through for the update loop."""
        self.target.update(*args, **kwargs)

    def draw(self, screen: pygame.Surface) -> None:
        """Default pass-through for the draw loop."""
        self.target.draw(screen)
 