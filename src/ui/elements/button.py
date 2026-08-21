from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any
import pygame
#from ..utils import align_rect
from .state_element import StateElement
from .base_element import UIElement

if TYPE_CHECKING:
    from src.custom_types import Pos

class Button(StateElement):
    def __init__(self, rect: pygame.Rect, 
                 function: Callable | None = None,
                 base_visual: UIElement | None = None, 
                 content: UIElement | None = None) -> None:
        super().__init__(rect, base_visual)
        self.function = function
        self.content = content 

    def update(self, mouse_pos: Pos | None = None) -> None:
        super().update(mouse_pos)
        if self.content:
            self.content.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible: 
            return
        super().draw(screen)
        if self.content:
            self.content.draw(screen)

    def is_click(self, mouse_pos: Pos) -> bool:
        return self.is_visible and self.rect.collidepoint(mouse_pos)
    
    def handle_click(self) -> Any:
        if self.function:   
            return self.function()
        
    def __getattr__(self, attr: str) -> Any:
        if self.content is None:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")
        return getattr(self.content, attr)
  