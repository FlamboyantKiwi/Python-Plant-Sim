from __future__ import annotations
from typing import TYPE_CHECKING, cast

import pygame

if TYPE_CHECKING:
    from custom_types import UIElement

class UIGroup(pygame.sprite.Group):
    """ A custom Pygame Group specifically designed to handle UI elements."""

    @property
    def elements(self) -> list['UIElement']:
        """Returns a strictly-typed list of UI elements for Pylance."""
        # We cast the entire list at once, using the string forward-reference!
        return cast(list['UIElement'], self.sprites())
    
    def draw(self, screen: pygame.Surface) -> None:
        """Overrides the default Pygame draw to use our custom UIElement.draw() methods."""
        for element in self.elements:
            element.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Passes click events down to the elements."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for element in reversed(self.elements):
                if element.is_click(event.pos):
                    element.handle_click()
                    return True
                    
        return False