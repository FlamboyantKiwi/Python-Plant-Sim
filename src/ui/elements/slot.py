from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .button import Button
from .textbox import TextBox

if TYPE_CHECKING:
    from src.custom_types import Item, Pos

    from .base_element import UIElement

class Slot(Button):
    def __init__(self, rect: pygame.Rect, index: int, base_visual: UIElement) -> None:
        super().__init__(rect, base_visual=base_visual)
        
        self.index = index
        self.item: Item | None = None 
        self.last_count = 0
        self.price: int | None = None
        
        # COMPONENT: Stack Count
        self.info_text = TextBox(
            rect=self.rect.inflate(-4, -4), 
            text="", config="SLOT", align="bottomright"
        )
        self.info_text.is_visible = False

    def set_item(self, item: Item | None) -> None:
        """Updates the slot's data."""
        current_count = item.count if item else 0
        
        # Check if it's a completely new item, OR if the existing item's count changed
        if self.item != item or self.last_count != current_count:
            self.item = item
            self.last_count = current_count
            self._update_text()
            
    def set_price(self, price: int) -> None:
        """Sets the slot to Shop Mode and remembers the price."""
        self.price = price
        self._update_text()
        
    def _update_text(self) -> None:
        """Internal helper to figure out what text to display."""
        if self.item is None:
            self.info_text.set_text("")
            self.info_text.is_visible = False
            return

        # PRIORITY 1: Shop Price
        if self.price is not None:
            self.info_text.set_text(f"£{self.price}")
            self.info_text.is_visible = True
            
        # PRIORITY 2: Stack Count
        elif self.item.max_stack > 1:
            self.info_text.set_text(self.item.count)
            self.info_text.is_visible = True
            
        # PRIORITY 3: Nothing (Unstackable item in a normal inventory)
        else:
            self.info_text.set_text("") 
            self.info_text.is_visible = False
    
    def update(self, mouse_pos: Pos | None = None) -> None:
        """Update states and the child text box."""
        super().update(mouse_pos)
        self.info_text.update()
       
    def draw(self, screen: pygame.Surface) -> None:
        # Draw Background (Managed by parent: Button)
        super().draw(screen)

        # Draw Item Content
        if self.item:
            # Center the item image
            item_rect = self.item.image.get_rect(center=self.rect.center)
            screen.blit(self.item.image, item_rect)
            #draw text on top of item 
            self.info_text.draw(screen)
   