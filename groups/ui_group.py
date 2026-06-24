from __future__ import annotations
from typing import TYPE_CHECKING, cast

import pygame

if TYPE_CHECKING:
    from custom_types import UIElement, Pos

class UIGroup(pygame.sprite.Group):
    """A custom Pygame Group specifically designed to handle dynamic and wrapped UI elements."""

    @property
    def elements(self) -> list[UIElement]:
        """Returns a strictly-typed list of UI elements or wrappers for Pylance."""
        # We cast the entire list at once, using the string forward-reference!
        return cast("list[UIElement]", self.sprites())
    
    def update(self, mouse_pos: Pos | None = None) -> None:
        """Broadcasts the current mouse position to all elements to drive hover and state logic."""
        for element in self.elements:
            element.update(mouse_pos)
    
    def draw(self, surface: pygame.Surface, bgsurf: pygame.Surface | None = None, special_flags: int = 0) -> list[pygame.Rect]:
        """ Overrides the default Pygame draw to safely render elements and dynamic wrappers.
        Signature matches pygame.sprite.Group exactly to satisfy static type checkers."""
        # Run your custom draw loop using the proper 'surface' argument
        for element in self.elements:
            element.draw(surface)
            
        # Return an empty list of Rects to satisfy the expected List[Rect] return type
        return []

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Passes click events down to the elements."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for element in reversed(self.elements):
                if element.is_click(event.pos):
                    element.handle_click()
                    return True
                    
        return False