from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from typing import Any
    from src.custom_types import Pos

class UIElement(pygame.sprite.Sprite):
    """ Base class for all UI components. Represents a physical space and an optional static visual. """
    def __init__(self, rect: pygame.Rect, surface: pygame.Surface | None = None) -> None:
        super().__init__()
        self.rect = rect
        self.is_visible = True
        self.image = surface
        
    def draw(self,screen: pygame.Surface) -> None:
        # Only draw if we have a valid surface
        if self.is_visible and self.image:
            screen.blit(self.image, self.rect)

    def update(self, mouse_pos: Pos | None = None) -> None:
        pass

    def is_click(self, mouse_pos: Pos) -> bool:
        return False 

    def handle_click(self) -> Any:
        return None

    def copy_image(self) -> pygame.Surface:
        """ Safely returns a copy of the element's surface. 
        Satisfies type checkers and prevents runtime crashes if the image is missing."""
        if self.image is not None:
            return self.image.copy()
        
        # Fallback: Return a blank, transparent surface matching the rect's dimensions
        return pygame.Surface(self.rect.size, pygame.SRCALPHA)
   