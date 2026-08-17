from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from src.core import Log
from src.ui import UIFactory
from src.ui import InventoryUI, Inventory
from src.core import calc_pos_rect
from src.settings import WIDTH, HEIGHT, DRAG_DROP_THRESHOLD

if TYPE_CHECKING:
    from src.custom_types import Pos, Item
    from src.core import controls

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
    
    def get_clicked_index(self, pos: 'Pos') -> int | None:
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
