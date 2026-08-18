from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.ui.ui_factory import UIFactory
from src.ui.elements import UIElement

if TYPE_CHECKING:
    from src.custom_types import Slot, Pos, Inventory


class InventoryUI(UIElement):
    """Handles all drawing and clicking for a grid of slots."""
    def __init__(self, rect:pygame.Rect, inventory_data: Inventory, columns:int=4, slot_size:int=40, padding:int=5) -> None:
        super().__init__(rect)
        self.data: Inventory = inventory_data # Link to the pure data
        
        # Calculate the exact width of the slots + gaps
        grid_width = (columns * slot_size) + ((columns - 1) * padding)
        
        # Reuse vertical stack math pattern: Center X, Top Y
        start_x = self.rect.centerx - (grid_width // 2)
        start_y = self.rect.y + padding
        
        # Setup Slots using the perfectly centered starting position
        self.slots: list[Slot] = UIFactory.create_grid(
            factory=UIFactory.bordered_slot,
            start_pos=(start_x, start_y),
            columns=columns,
            item_size=(slot_size, slot_size),
            gap=(padding, padding),
            data=self.data.max_size
        )

        self.tooltip = UIFactory.text(
            rect=pygame.Rect(0, 0, 0, 0), # Position will be updated dynamically
            text="", 
            config="HUD", # Ensure this matches a config in your ASSETS
            align="midbottom"
        )

    def update(self, mouse_pos:Pos|None=None) -> None:
        """ Syncs the visual slots with the backend data and runs hover logic. """
        super().update(mouse_pos)
        hovered_item_name = ""
        
        # Update all slots and check for hovers
        for i, slot in enumerate(self.slots):
            slot.set_item(self.data.items[i]) 
            slot.update(mouse_pos)
            
            if slot.is_hovered and slot.item:
                hovered_item_name = slot.item.name
                
        # 3. Update Tooltip text and position
        if hovered_item_name:
            self.tooltip.set_text(hovered_item_name)
            self.tooltip.is_visible = True
            
            if mouse_pos:
                # Make the tooltip follow the mouse, offset slightly up and to the right
                self.tooltip.rect.midbottom = (mouse_pos[0] + 15, mouse_pos[1] - 10)
        else:
            self.tooltip.is_visible = False
            
        self.tooltip.update(mouse_pos)

    def draw(self, screen:pygame.Surface) -> None:
        # Draw main background
        super().draw(screen)
        
        # Draw slots
        for slot in self.slots:
            slot.draw(screen)

    def is_click(self, mouse_pos:Pos) -> bool:
        """ Checks if the overall inventory panel was clicked. """
        return self.is_visible and self.rect.collidepoint(mouse_pos)

    def click(self, mouse_pos:Pos) -> int | None:
        """ Returns the index of the specific slot that was clicked, or None. """
        for slot in self.slots:
            if slot.is_click(mouse_pos):
                return slot.index
        return None
   