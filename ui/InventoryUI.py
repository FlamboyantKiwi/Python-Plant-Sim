import copy, pygame
from ui.ui_elements import UIElement, TextBox, Slot
from entities.items import Item, ItemFactory
from Assets.asset_data import ITEMS
from settings import SHOP_MENU

class Inventory:
    """Pure data structure. No Pygame/UI logic here."""
    def __init__(self, max_size=16):
        self.max_size = max_size
        self.items:list[Item|None] = [None] * max_size # Just stores Item objects

    def add_item(self, new_item):
        """ Handles stacking and splitting large stacks into multiple empty slots. """
        remaining = new_item.count
        
        # 1. Try to add to existing stacks first
        if new_item.stack_size > 1:
            for i in range(self.max_size):
                item = self.items[i]
                if item and item.name == new_item.name:
                    space_left = item.stack_size - item.count
                    if space_left > 0:
                        amount_to_add = min(remaining, space_left)
                        item.count += amount_to_add
                        remaining -= amount_to_add
                        
                    if remaining <= 0:
                        return True # Everything was stacked

        # 2. Spill over into empty slots
        for i in range(self.max_size):
            if self.items[i] is None:
                to_add = copy.copy(new_item)
                count = min(remaining, to_add.stack_size)
                to_add.count = count
                self.items[i] = to_add
                remaining -= count
                
                if remaining <= 0:
                    return True # Everything found a slot
                    
        # Return False if the inventory filled up before everything could be added
        return False

    def remove_item(self, item_name, amount=1):
        """Removes an item by name, starting from the end of the inventory first."""
        remaining = amount
        
        # Iterate backwards
        for i in range(self.max_size - 1, -1, -1):
            item = self.items[i]
            if item and item.name == item_name:
                if item.count > remaining:
                    item.count -= remaining
                    return True
                else:
                    # Consumed whole slot
                    remaining -= item.count
                    self.items[i] = None # Clear slot in data
                    
                if remaining <= 0: 
                    return True
                    
        return False # Didn't have enough of the item to remove the full amount

class InventoryUI(UIElement):
    """Handles all drawing and clicking for a grid of slots."""
    def __init__(self, rect, inventory_data: Inventory, columns=4, slot_size=40, padding=5):
        super().__init__(rect)
        self.data = inventory_data # Link to the pure data
        self.slots = []
        
        # 1. Setup Slots using Slots factory Method
        self.slots = Slot.create_grid(
            max_size=self.data.max_size, columns=columns,
            start_pos=(self.rect.x + padding, self.rect.y + padding),
            slot_size=slot_size, padding=padding)
        
        #Setup tooltip
        self.tooltip = TextBox(
            rect=pygame.Rect(self.rect.centerx, self.rect.top - 25, 0, 0),
            text_getter=self._get_tooltip_text,
            text="", config="HUD", align="midbottom"
        )

    def _get_tooltip_text(self):
        """ Feeds the hovered item's name to the TextBox """
        hovered_slot = next((s for s in self.slots if getattr(s, 'is_hovered', False)), None)
        if hovered_slot and hovered_slot.item:
            return hovered_slot.item.name
        return ""

    def update(self, mouse_pos=None):
        """ Syncs the visual slots with the backend data and runs hover logic. """
        super().update(mouse_pos)
        
        for i, slot in enumerate(self.slots):
            # Continually ensure the UI matches the data list
            slot.set_item(self.data.items[i]) 
            slot.update(mouse_pos)
            
        self.tooltip.update()

    def draw(self, screen):
        # Draw main background
        super().draw(screen)
        
        # Draw slots
        for slot in self.slots:
            slot.draw(screen)
            
        # Draw tooltip
        self.tooltip.draw(screen)

    def is_click(self, mouse_pos):
        """ Checks if the overall inventory panel was clicked. """
        if not self.is_visible: return False
        return self.rect.collidepoint(mouse_pos)

    def click(self, mouse_pos):
        """ Returns the index of the specific slot that was clicked, or None. """
        for slot in self.slots:
            if slot.is_click(mouse_pos):
                return slot.index
        return None
    
class ShopMenu:
    """Controller for the Shop. Uses Composition to manage data and UI."""
    def __init__(self, player, data, columns=4, max_size=16):
        self.player = player
        self.shop_data = data
        self.is_open = False
        self.rect = SHOP_MENU

        # Background visual
        self.background = UIElement(self.rect, image_file="SHOP_MENU")

        # The Pure Data
        self.inventory_data = Inventory(max_size=max_size)
        
        # The Visual Grid
        self.ui_grid = InventoryUI(
            rect=self.rect, 
            inventory_data=self.inventory_data, 
            columns=columns, 
            slot_size=70, 
            padding=20
        )
        
        title_string = self.shop_data.store_name if self.shop_data else "Shop"
        
        self.title_box = TextBox(
            rect=pygame.Rect(self.rect.centerx, self.rect.top + 10, 0, 0),
            text=title_string,
            config="HUD", 
            align="midtop"
        )

        self.populate_shop()

    def populate_shop(self):
        """ Reads IDs from shop_data and fills the backend data structure. """
        if not self.shop_data: return

        for i, item_id in enumerate(self.shop_data.items_ids):
            if i >= self.inventory_data.max_size: break

            # Assuming ITEMS is a dict of valid IDs
            if item_id not in ITEMS:
                print(f"Shop Warning: Item ID '{item_id}' not found.")
                continue

            # Create the item and insert it straight into the pure data list
            new_item = ItemFactory.create(item_id, count=1)
            self.inventory_data.items[i] = new_item
            
            self.ui_grid.slots[i].set_price(new_item.data.buy_price)

    def update(self, mouse_pos=None):
        """ Runs the UI updates and re-applies price tags. """
        if not self.is_open: return
        
        # This syncs the UI with the data (and normally sets text to stack count)
        self.ui_grid.update(mouse_pos)
        self.title_box.update()

    def draw(self, screen):
        if not self.is_open: return
        
        # Draw Background Image
        self.background.draw(screen)

        # Draw Title
        self.title_box.draw(screen)
        
        # Draw the Grid UI
        self.ui_grid.draw(screen)
  
    def handle_click(self, pos):
        """Handles interaction. Returns a string action code if the State needs to react."""
        if not self.is_open: return False

        # Let the UI grid tell us the index of what was clicked
        clicked_index = self.ui_grid.click(pos)
        
        if clicked_index is not None:
            # Grab the actual item object from the data layer using the index
            item = self.inventory_data.items[clicked_index]
            if item:
                return self.try_buy_item(item)
                
        return False

    def try_buy_item(self, item):
        """Validates and executes the purchase logic"""
        cost = item.data.buy_price
        
        # Check Money
        if self.player.money < cost:
            print(f"Cannot afford {item.name}! (Cost: {cost}, Have: {self.player.money})")
            return False

        # Create a fresh copy to give to the player
        import copy
        player_item = copy.copy(item)
        player_item.count = 1 
        
        # Try to Add item to player's actual data inventory
        if self.player.inventory.add_item(player_item):
            self.player.money -= cost
            print(f"Bought {player_item.name} for {cost}g.")
            return True
            
        print("Transaction failed (Inventory full).")
        return False