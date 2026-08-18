from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from .base_element import UIElement

if TYPE_CHECKING:
    from src.custom_types import Pos

class StateElement(UIElement):
    """Base class for anything that reacts to hovers or clicks."""
    def __init__(self, rect: pygame.Rect, base_visual: UIElement | None = None) -> None:
        super().__init__(rect) 
        self.is_hovered = False
        self.is_active = False
        self.image = base_visual.copy_image() if base_visual else pygame.Surface(rect.size, pygame.SRCALPHA)
        
    def update(self, mouse_pos: Pos | None = None) -> None:
        if mouse_pos:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
            