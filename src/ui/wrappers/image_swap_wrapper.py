from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from .base_wrapper import BaseWrapper

if TYPE_CHECKING:
    from src.ui.elements import StateElement
    from src.custom_types import Pos

class ImageSwapWrapper(BaseWrapper):
    """Dynamically swaps the underlying image of a StateElement based on state."""
    def __init__(self, target: StateElement, 
                 surf_normal: pygame.Surface, 
                 surf_hover: pygame.Surface | None = None, 
                 surf_active: pygame.Surface | None = None):
        super().__init__(target)
        self.surf_normal = surf_normal
        # Fallbacks
        self.surf_hover = surf_hover if surf_hover else surf_normal
        self.surf_active = surf_active if surf_active else self.surf_hover

    def update(self, mouse_pos: Pos | None = None) -> None:
        # Update the target so it calculates its state
        self.target.update(mouse_pos)

        # Swap the target's image surface based on new state
        if self.target.is_active:
            self.target.image = self.surf_active
        elif self.target.is_hovered:
            self.target.image = self.surf_hover
        else:
            self.target.image = self.surf_normal
 