from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .inventory_controller import InventoryController
    from .inventory_manager import InventoryManager
    from src.custom_types import Item
    
class DragController:
    """Handles mouse tracking, drag thresholds, and visual state for dragging items."""
    def __init__(self, manager: 'InventoryManager') -> None:
        self.manager = manager
        self.cursor_item: Item | None = None
        
        # Bundled drag state
        self.drag_origin: tuple['InventoryController', int] | None = None
        self.drag_start_pos: tuple[int, int] | None = None
        self.is_dragging: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Routes mouse events to their specific lifecycle handlers."""
        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, 'button', 1) == 1:
            return self._handle_mouse_down(event.pos)
            
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONUP and getattr(event, 'button', 1) == 1:
            return self._handle_mouse_up(event.pos)
            
        return False

    def _handle_mouse_down(self, pos: tuple[int, int]) -> bool:
        """Phase 1: Select slot and prepare for a potential drag."""
        slot_data = self.manager.get_slot_at(pos)
        
        if slot_data is not None:
            ctrl, idx = slot_data
            ctrl.set_active_slot(idx)
            
            if ctrl.data.items[idx]: 
                self.drag_origin = (ctrl, idx)
                self.drag_start_pos = pos
                self.is_dragging = False
            return True
        return False

    def _handle_mouse_motion(self, pos: tuple[int, int]) -> bool:
        """Phase 2: Detect movement threshold and lift item into cursor."""
        if self.drag_origin and self.drag_start_pos and not self.is_dragging:
            dx = pos[0] - self.drag_start_pos[0]
            dy = pos[1] - self.drag_start_pos[1]
            
            if (dx**2 + dy**2) > 25: 
                ctrl, idx = self.drag_origin
                self.cursor_item = ctrl.data.items[idx]
                ctrl.data.items[idx] = None 
                self.is_dragging = True
        return False

    def _handle_mouse_up(self, pos: tuple[int, int]) -> bool:
        """Phase 3: Drop the item, snap to closest, or return to origin."""
        if not self.is_dragging:
            self.drag_origin = None
            self.drag_start_pos = None
            return False

        target_data = self.manager.get_slot_at(pos)

        # If dropped in the void, try to snap to the closest slot
        if not target_data:
            target_data = self.manager.find_closest_slot(pos)

        # Let the InventoryManager handle the actual data manipulation
        if target_data is not None:
            target_ctrl, target_idx = target_data
            self.manager.drop_item(self, target_ctrl, target_idx)
        else:
            self.manager.return_to_origin(self)

        self.is_dragging = False
        self.drag_origin = None
        self.drag_start_pos = None
        return True

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        """Draws the item floating on the mouse."""
        if self.cursor_item:
            rect = self.cursor_item.image.get_rect(center=mouse_pos)
            screen.blit(self.cursor_item.image, rect)
