from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.ui.ui_factory import UIFactory
from src.ui.ui_elements import UIElement
from src.ui.wrappers import Tooltip
from src.entities.items import Item, create_item
from src.settings import SHOP_GRID_OFFSET_Y, SHOP_MENU
from src.core import Log

if TYPE_CHECKING:
    from src.custom_types import Slot, Pos, Player, ShopData

class Inventory:
    """Pure data structure. No Pygame/UI logic here."""
    def __init__(self, max_size:int=16) -> None:
        self.max_size:int = max_size
        self.items:list[Item|None] = [None] * max_size # Just stores Item objects

    def get_amount(self, item_name: str) -> int:
        """Helper: Quickly get the total count of a specific item across all stacks."""
        return sum(item.count for item in self.items if item and item.name == item_name)

    def add_item(self, new_item:Item) -> bool:
        """ Handles stacking and splitting large stacks into multiple empty slots. """
        remaining = new_item.count
        
        # Try to add to existing stacks first
        if new_item.max_stack > 1:
            for item in self.items:
                if item and item.name == new_item.name and item.count < item.max_stack:
                    added = min(remaining, item.max_stack - item.count)
                    item.count += added
                    remaining -= added
                    
                    if remaining <= 0: 
                        return True # Fully stacked

        # Spill over into empty slots
        for i in range(self.max_size):
            if self.items[i] is None:
                to_add = new_item.copy_one()
                to_add.count = min(remaining, to_add.max_stack)
                self.items[i] = to_add
                remaining -= to_add.count
                
                if remaining <= 0:
                    return True # Everything found a slot
                    
        # Return False if the inventory filled up before everything could be added
        return False

    def remove_item(self, item_name:str, amount:int=1) -> bool:
        """Removes an item by name, starting from the end of the inventory first."""        
        #make sure we have enough BEFORE removing
        if self.get_amount(item_name) < amount:
            return False
        # Iterate backwards
        for i in range(self.max_size - 1, -1, -1):
            item = self.items[i]
            if item and item.name == item_name:
                if item.count > amount:
                    item.count -= amount
                    return True
                else:
                    # Consumed whole slot
                    amount -= item.count
                    self.items[i] = None # Clear slot in data
                    
                if amount <= 0: 
                    return True
                    
        return False # Didn't have enough of the item to remove the full amount

    def transfer_to(self, target_inventory: 'Inventory', item_name: str, amount: int) -> bool:
        """Programmatically moves an item from this inventory to another."""
        if self.get_amount(item_name) < amount:
            return False # We don't have enough to give

        # Create a detached copy of the item to transfer
        for item in self.items:
            if item and item.name == item_name:
                item_to_give = item.copy_one()
                item_to_give.count = amount
                break
                
        # Try to put it in the target's inventory
        if target_inventory.add_item(item_to_give):
            # If successful, remove it from our own inventory
            self.remove_item(item_name, amount)
            return True
            
        return False # Target inventory was full!

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
    
class ShopMenu:
    """Controller for the Shop. Uses Composition to manage data and UI."""
    def __init__(self, player:Player, data:ShopData|None, columns:int=4, max_size:int=16) -> None:
        self.player:Player = player
        self.shop_data:ShopData|None = data
        self.is_open:bool = False
        self.rect:pygame.Rect = SHOP_MENU

        # Background visual
        self.background = UIFactory.static_border_element(
            rect=self.rect, 
            colour="MenuBG",              # The dark grey used in your main menu
            border_colour="ButtonBorder", # A lighter grey for the rim
            thickness=3
        )

        # The Pure Data
        self.inventory_data:Inventory = Inventory(max_size=max_size)

        grid_rect = self.rect.copy()
        grid_rect.y += SHOP_GRID_OFFSET_Y
        
        # The Visual Grid
        base_grid = UIFactory.inventory_ui(
            rect=grid_rect, 
            inventory_data=self.inventory_data, 
            columns=columns, 
            slot_size=70, 
            padding=20
        )
        
        # Create the detached tooltip box
        tooltip_box = UIFactory.text(
            rect=pygame.Rect(self.rect.centerx, self.rect.top - 25, 0, 0),
            text="", 
            config="HUD", 
            align="midbottom"
        )
        
        # Wrap them together so self.ui_grid acts as a single functional unit
        self.ui_grid:Tooltip = Tooltip(base_grid, tooltip_box)
        
        title_string = self.shop_data.store_name if self.shop_data else "Shop"
        
        self.title_box:UIElement = UIFactory.text(
            rect=pygame.Rect(self.rect.centerx, self.rect.top + 10, 0, 0),
            text=title_string,
            config="HUD", 
            align="midtop"
        )

        self.populate_shop()

    def populate_shop(self) -> None:
        """ Reads IDs from shop_data and fills the backend data structure. """
        if not self.shop_data: 
            return

        for i, item_id in enumerate(self.shop_data.items_ids):
            if i >= self.inventory_data.max_size: 
                break

            # Create the item and insert it straight into the pure data list
            new_item = create_item(item_id, count=1)
            self.inventory_data.items[i] = new_item
            
            self.ui_grid.slots[i].set_price(new_item.data.buy_price)

    def update(self, mouse_pos:Pos|None=None) -> None:
        """ Runs the UI updates and re-applies price tags. """
        if not self.is_open: 
            return
        
        # This syncs the UI with the data (and normally sets text to stack count)
        self.ui_grid.update(mouse_pos)
        self.title_box.update()

    def draw(self, screen:pygame.Surface) ->None:
        if not self.is_open: 
            return
        
        # Draw Background Image
        self.background.draw(screen)

        # Draw Title
        self.title_box.draw(screen)
        
        # Draw the Grid UI
        self.ui_grid.draw(screen)
  
    def handle_click(self, pos:Pos) -> bool:
        """Handles interaction. Returns a string action code if the State needs to react."""
        if not self.is_open: 
            return False

        # Let the UI grid tell us the index of what was clicked
        clicked_index = self.ui_grid.click(pos)
        
        if clicked_index is not None:
            # Grab the actual item object from the data layer using the index
            item = self.inventory_data.items[clicked_index]
            if item:
                return self.try_buy_item(item)
                
        return False

    def try_buy_item(self, item:Item) -> bool:
        """Validates and executes the purchase logic"""
        cost = item.data.buy_price
        
        # Check Money
        if self.player.money < cost:
            Log.error(f"Cannot afford {item.name}! (Cost: {cost}, Have: {self.player.money})")
            return False

        # Create a fresh copy to give to the player
        player_item = item.copy_one()
        
        # Try to Add item to player's actual data inventory
        if self.player.inventory.data.add_item(player_item):
            self.player.money -= cost
            Log.info(f"Bought {player_item.name} for {cost}g.")
            return True
            
        Log.error("Transaction failed (Inventory full).")
        return False