from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from .base_wrapper import BaseWrapper

if TYPE_CHECKING:
    from src.custom_types import Pos
    from src.ui.elements import TextBox
    
class TooltipWrapper(BaseWrapper):
    """Wraps an InventoryUI to display a tooltip that follows the mouse for hovered items."""
    def __init__(self, target: Any, tooltip_box: TextBox, offset: tuple[int, int] = (15, 15)) -> None:
        super().__init__(target)
        self.tooltip = tooltip_box
        self.offset = offset  # Distance from the cursor to draw the tooltip

    def update(self, mouse_pos: Pos | None = None) -> None:
        # Update the underlying inventory UI (syncs slots and handles their hover states)
        self.target.update(mouse_pos)

        # Check for hovered items
        hovered_item_name = ""
        if mouse_pos:
            for slot in self.target.slots:
                if slot.is_hovered and slot.item:
                    hovered_item_name = slot.item.name
                    break  # Found the hovered item, no need to keep checking

        # Update the tooltip text and state
        self.tooltip.set_text(hovered_item_name)
        self.tooltip.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the main inventory grid first
        self.target.draw(screen)
        
        # Draw the tooltip on top
        self.tooltip.draw(screen)

        