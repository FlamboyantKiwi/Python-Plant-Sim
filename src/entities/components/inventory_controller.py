from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.config import HEIGHT, WIDTH
from src.ui import UIFactory, calc_pos_rect
from src.utils import Log

from ..inventory_data import Inventory

if TYPE_CHECKING:
    from src.custom_types import Item, Pos

class InventoryController:
    """Manages data, UI, and interactions for an entity's inventory."""
    def __init__(self, size: int = 8, slot_size: int = 50, padding: int = 5) -> None:
        self.size = size
        self.data = Inventory(max_size=size)
        self.active_slot_index = 0
        
        # Calculate UI Rect
        required_width = size * (slot_size + padding) + padding
        required_height = slot_size + padding * 2
        self.rect = calc_pos_rect(
            required_width, required_height, WIDTH, HEIGHT,
            y_offset=((HEIGHT - required_height) // 2) - 10
        )
        
        #Setup Background panel
        self.background = UIFactory.solid_element(self.rect, "SLOT")

        # Setup Slots directly via UIFactory
        self.slots = UIFactory.create_grid(
            factory=UIFactory.bordered_slot,
            start_pos=(self.rect.x + padding, self.rect.y + padding),
            columns=size,
            item_size=(slot_size, slot_size),
            gap=(padding, padding),
            data=self.size
        )
        
        # Highlight initial slot
        self.slots[self.active_slot_index].is_active = True

        # Setup Tooltip
        self.tooltip = UIFactory.text(
            rect=pygame.Rect(self.rect.centerx, self.rect.top - 10, 0, 0),
            text="", 
            config="HUD", 
            align="midbottom"
        )

    def set_active_slot(self, index: int) -> None:
        """Safely updates the active slot and handles UI highlighting."""
        if 0 <= index < self.size:
            self.slots[self.active_slot_index].is_active = False
            self.active_slot_index = index
            self.slots[self.active_slot_index].is_active = True

    def get_active_item(self) -> Item | None:
        """Returns the item currently selected in the hotbar."""
        return self.data.items[self.active_slot_index]

    def consume_active_item(self) -> None:
        """Destroys the active item if its count drops to 0."""
        item = self.get_active_item()
        if item and item.count <= 0:
            self.data.items[self.active_slot_index] = None
            Log.info("Item consumed entirely.")

    def handle_event(self, event: pygame.event.Event, controls_map) -> None:
        """Listens for hotbar hotkeys."""
        if event.type == pygame.KEYDOWN and event.key in controls_map.slots:
            self.set_active_slot(controls_map.slots[event.key])

    def handle_click(self, pos: Pos) -> bool:
        """Processes clicks inside the inventory panel."""
        if not self.rect.collidepoint(pos):
            return False

        for slot in self.slots:
            if slot.is_click(pos):
                self.set_active_slot(slot.index)
                return True
        return False
    
    def get_clicked_index(self, pos: Pos) -> int | None:
        """Returns the index of the slot clicked, or None."""
        if not self.rect.collidepoint(pos):
            return None

        for slot in self.slots:
            if slot.is_click(pos):
                return slot.index
        return None
        
    def update(self, mouse_pos: Pos | None = None) -> None:
        hovered_item_name = ""
        
        # Update slots and sync data
        for i, slot in enumerate(self.slots):
            slot.set_item(self.data.items[i]) 
            slot.update(mouse_pos)
            
            # Check for tooltip hover
            if slot.is_hovered and slot.item:
                hovered_item_name = slot.item.name
                
        # Manage Tooltip state
        if hovered_item_name:
            self.tooltip.set_text(hovered_item_name)
            self.tooltip.is_visible = True
        else:
            self.tooltip.is_visible = False
            
        self.tooltip.update()
        
    def draw(self, screen: pygame.Surface) -> None:
        # Draw base panel
        self.background.draw(screen)
        
        # Draw slots
        for slot in self.slots:
            slot.draw(screen)
            
        # Draw tooltip last (always on top)
        if self.tooltip.is_visible:
            self.tooltip.draw(screen)
