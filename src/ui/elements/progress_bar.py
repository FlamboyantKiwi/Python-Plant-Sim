from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import pygame
from .base_element import UIElement

if TYPE_CHECKING:
    from src.custom_types import Pos


class ProgressBar(UIElement):
    """A reusable progress controller that scales and aligns injected UIElements."""
    def __init__(self, rect: pygame.Rect, 
                 bg_element: UIElement,
                 fill_element: UIElement,
                 percentage: float = 1.0, 
                 value_getter: Callable[[], float] | None = None,
                 alignment: str = "left", is_horizontal: bool|None = None) -> None:
        super().__init__(rect)
        self.bg_element = bg_element
        self.fill_element = fill_element
        self.alignment = alignment.lower()
        
        self.percentage = max(0.0, min(1.0, percentage))
        self.value_getter = value_getter

        # Cache the original surface so we can scale it dynamically without distortion
        self._fill_surface_base = self.fill_element.copy_image()

        # Deduce scaling axis based on proportions, unless explicitly overridden
        self.is_horizontal = is_horizontal if is_horizontal is not None else (self.rect.width >= self.rect.height)
        # Track the dynamic size (width or height depending on alignment) to prevent redundant scaling
        self._cached_size: int = -1
        self._update_fill_rect()

    def _update_fill_rect(self) -> None:
        """Recalculates dimensions, scales the surface, and anchors it based on alignment."""
        ratio = max(0.0, min(1.0, self.percentage))
        
        # Determine dimensions based on axis (deduced or overriden)
        if self.is_horizontal:
            new_w = int(self.rect.width * ratio)
            new_h = self.rect.height
            dynamic_size = new_w
        else:
            new_w = self.rect.width
            new_h = int(self.rect.height * ratio)
            dynamic_size = new_h

        # Only mutate the surface and rect if the pixel size actually changed
        if dynamic_size != self._cached_size:
            self._cached_size = dynamic_size
            
            if dynamic_size > 0:
                # Scale the original surface to the new dimensions
                self.fill_element.image = pygame.transform.scale(
                    self._fill_surface_base, 
                    (new_w, new_h)
                )
                self.fill_element.rect.size = (new_w, new_h)
                
                # Dynamic Anchoring: grabs the point from the background rect and applies it to the fill rect
                try:
                    anchor_point = getattr(self.rect, self.alignment)
                    setattr(self.fill_element.rect, self.alignment, anchor_point)
                except AttributeError:
                    # Fallback if an invalid Pygame anchor string was provided
                    self.fill_element.rect.topleft = self.rect.topleft

    def update(self, mouse_pos: Pos | None = None) -> None:
        """Polls the value getter and updates the fill block only when data changes."""
        if self.value_getter:
            val = max(0.0, min(1.0, self.value_getter()))
            if val != self.percentage:
                self.percentage = val
                self._update_fill_rect()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible:
            return
            
        self.bg_element.draw(screen)
        
        # Only draw the fill if its dynamic dimension is greater than 0
        if self._cached_size > 0:
            self.fill_element.draw(screen)
