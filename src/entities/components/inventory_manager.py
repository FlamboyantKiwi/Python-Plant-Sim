
from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
from src.settings import DRAG_DROP_THRESHOLD
from .drag_controller import DragController

if TYPE_CHECKING:
    from .inventory_controller import InventoryController

class InventoryManager:
    """Manages open inventories and executes item data manipulation (stacking/swapping)."""
    def __init__(self) -> None:
        self.open_controllers: list['InventoryController'] = []
        self.drag_controller = DragController(self)

    # --- EXPOSED API FOR HUD/PLAYER ---

    def handle_event(self, event: pygame.event.Event) -> bool:
        return self.drag_controller.handle_event(event)

    def draw_cursor_item(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        self.drag_controller.draw(screen, mouse_pos)

    def open_inventory(self, controller: 'InventoryController') -> None:
        if controller not in self.open_controllers:
            self.open_controllers.append(controller)

    def close_inventory(self, controller: 'InventoryController') -> None:
        if controller in self.open_controllers:
            self.open_controllers.remove(controller)

    # --- LOOKUP UTILITIES FOR THE DRAG CONTROLLER ---
    def get_slot_at(self, pos: tuple[int, int]) -> tuple['InventoryController', int] | None:
        for controller in reversed(self.open_controllers):
            idx = controller.get_clicked_index(pos)
            if idx is not None:
                return controller, idx
        return None

    def find_closest_slot(self, drop_pos: tuple[int, int]) -> tuple['InventoryController', int] | None:
        best_target = None
        min_dist = DRAG_DROP_THRESHOLD

        for ctrl in self.open_controllers:
            for slot in ctrl.slots:
                cx, cy = slot.rect.center
                dist = ((cx - drop_pos[0])**2 + (cy - drop_pos[1])**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    best_target = (ctrl, slot.index)
                    
        return best_target

    # --- DATA MANIPULATION FOR THE DRAG CONTROLLER ---
    def drop_item(self, drag_ctrl: 'DragController', target_ctrl: 'InventoryController', target_idx: int) -> None:
        """Executes placing, stacking, or swapping data logic."""
        if not drag_ctrl.cursor_item:
            return

        target_item = target_ctrl.data.items[target_idx]

        # Try to Stack
        if target_item and drag_ctrl.cursor_item.name == target_item.name:
            space_left = target_item.max_stack - target_item.count
            if space_left > 0:
                moved = min(space_left, drag_ctrl.cursor_item.count)
                target_item.count += moved
                drag_ctrl.cursor_item.count -= moved

        # Swap if the cursor still holds an item
        if drag_ctrl.cursor_item and drag_ctrl.cursor_item.count > 0:
            target_ctrl.data.items[target_idx], drag_ctrl.cursor_item = drag_ctrl.cursor_item, target_ctrl.data.items[target_idx]
            
            # If swap resulted in holding a new item, snap it back
            if drag_ctrl.cursor_item:
                self.return_to_origin(drag_ctrl)
        else:
            drag_ctrl.cursor_item = None

    def return_to_origin(self, drag_ctrl: 'DragController') -> None:
        """Safely snaps the cursor item data back to its starting slot."""
        if not drag_ctrl.cursor_item or not drag_ctrl.drag_origin:
            return
            
        ctrl, idx = drag_ctrl.drag_origin
        if ctrl.data.items[idx] is None:
            ctrl.data.items[idx] = drag_ctrl.cursor_item
        else:
            ctrl.data.add_item(drag_ctrl.cursor_item) 
        drag_ctrl.cursor_item = None
