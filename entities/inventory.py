import pygame, copy

from settings import SHOP_MENU
from entities.items import Item, ItemFactory
from core.helper import draw_text
from core.types import ShopData, FontType
from Assets.asset_data import ITEMS
from ui.ui_elements import Slot, TextBox, UIElement
from core.asset_loader import AssetLoader


class Inventory:
    def __init__(self, max_size = 4, columns = 1, rect = None, slot_size = 40, padding = 5):
        #list of Item Objects
        self.max_size = max_size #total number of slots
        self.cols = columns

        #Inventory Visuals
        self.slot_size = slot_size
        self.padding = padding

        # Setup Grid Rect
        if rect is None: # If no rect is provided, create a minimal default one
            rows = (self.max_size + self.cols - 1) //self.cols
            default_width = columns * (self.slot_size + self.padding) + self.padding
            default_height = rows * (self.slot_size + self.padding) + self.padding
            self.rect = pygame.Rect(0, 0, default_width, default_height)
        else:
            self.rect = rect

        # Setup Slots
        self.slots = []
        for i in range(self.max_size):
            col = i % self.cols
            row = i // self.cols
            
            x = self.rect.x + self.padding + col * (self.slot_size + self.padding)
            y = self.rect.y + self.padding + row * (self.slot_size + self.padding)
            
            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            
            # Create our UI Slot object
            new_slot = Slot(slot_rect, i, self.slot_size)
            self.slots.append(new_slot)
            
        self.active_slot_index = -1

        # Placed slightly above the inventory top edge
        self.tooltip = TextBox(
            rect=pygame.Rect(self.rect.centerx, self.rect.top - 25, 0, 0),
            text_getter=self._get_tooltip_text,
            text="",config="HUD",align="midbottom") # Anchors text bottom-center to the rect position
    
    def draw(self, screen):
        """Draws all UI slots."""        
        # Draw Slots
        for slot in self.slots:
            slot.draw(screen)
            # Highlight Active Slot
            if slot.index == self.active_slot_index:
                pygame.draw.rect(screen, (255, 255, 255), slot.rect, 2)
        
        # Draw Name of hovered item
        self.tooltip.draw(screen)

    def update(self, pos):
        """Updates all UI slots (Hover effects, etc)."""
        for slot in self.slots:
            slot.update(pos)
        # Runs textBox's getter function, only re-renders if text changed
        self.tooltip.update()
        
    def _get_tooltip_text(self):
        """ Determining what the tooltip should say.
            Called automatically by the TextBox every frame."""
        # Check Hovered Slot
        hovered_slot = next((s for s in self.slots if s.is_hovered), None)
        
        if hovered_slot and hovered_slot.item:
            return hovered_slot.item.name
            
        # Fallback: Active Item Name
        active_item = self.get_active_item()
        if active_item:
            return active_item.name
            
        return "" # Default to empty
    
    def add_item(self, new_item:Item):
        """ Adds an item to the inventory. Handles stacking and splitting 
            large stacks into multiple slots automatically."""
        remaining = new_item.count
        
        #add to existing slots
        if new_item.stackable:
            for slot in self.slots:
                if slot.item and slot.item.name == new_item.name:
                    space_left = slot.item.stack_size - slot.item.count
                    if space_left > 0:
                        amount_to_add = min(remaining, space_left)
                        slot.item.count += amount_to_add
                        remaining -= amount_to_add
                        slot.set_item(slot.item) # Refresh visual
        for slot in self.slots:
            if remaining <= 0: break
            if slot.item is None:
                to_add = copy.copy(new_item)
                if new_item.stackable:  count = min(remaining, to_add.stack_size) 
                else:                   count = 1
                to_add.count = count
                slot.set_item(to_add)
                remaining -= count
        
        return remaining < new_item.count
    
    def remove_item(self, item_name, amount=1):
        """Removes an item by name, starting from the last slot."""
        remaining = amount
        # Iterate backwards to remove from end of inventory first
        for slot in reversed(self.slots):
            if slot.item and slot.item.name == item_name:
                if slot.item.count > remaining:
                    slot.item.count -= remaining
                    slot.set_item(slot.item) # Update text
                    return True
                else:
                    # Consumed whole slot
                    remaining -= slot.item.count
                    slot.set_item(None) # Clear slot
                    
                if remaining <= 0: return True
        return False
    
    def remove_if_empty(self, item):
        """ Checks if the provided item has run out (count <= 0).
            If so, clears the slot.
            If not, refreshes the slot visual (count text)."""
        # Find which slot actually holds this item object
        # We use 'is' to ensure we are looking at the exact same object instance
        target_slot = next((s for s in self.slots if s.item is item), None)
        
        if target_slot:
            if item.count <= 0:
                target_slot.set_item(None) # Clear the slot
                return True
            else:
                target_slot.set_item(item) # Refresh text (e.g. update 5 -> 4)
                
        return False
    
    def set_active_slot(self, index):
        """Sets the active slot, ensuring it's within bounds."""
        if 0 <= index < self.max_size:
            self.active_slot_index = index
            return True
        return False
    
    def get_active_item(self):
        if 0 <= self.active_slot_index < len(self.slots):
            return self.slots[self.active_slot_index].item
        return None

    def handle_click(self, pos):
        """Iterates through slots to see if one was clicked.
            Updates active_slot_index if true."""
        for slot in self.slots:
            if slot.is_click(pos):
                self.active_slot_index = slot.index
                print(f"Active slot changed to: {self.active_slot_index}")
                return True
        return False
   
class ShopMenu(Inventory):
    def __init__(self, player, data:ShopData, columns=4, max_size=16):
        super().__init__(max_size, columns, rect=SHOP_MENU, slot_size=70, padding=20)
        
        # Shop specific properties
        self.player = player
        self.shop_data = data
        self.is_open = False

        self.background = UIElement(self.rect, image_file="SHOP_MENU")
        self.populate_shop()

    def populate_shop(self):
        """ Reads IDs from shop_data and fills UI slots """
        # Check if shop_data exists
        if not self.shop_data: return

        for i, item_id in enumerate(self.shop_data.items_ids):
            # Don't overflow slots
            if i >= len(self.slots): break

            if item_id not in ITEMS:
                print(f"Shop Warning: Item ID '{item_id}' not found.")
                continue

            # Create the item and assign it directly to the slot
            new_item = ItemFactory.create(item_id, count=1)
            self.slots[i].set_item(new_item)
            self.slots[i].set_price(new_item.data.buy_price)
            
    def draw(self, screen):
        if not self.is_open: return
        
        # Draw Background Image
        self.background.draw(screen)

        title = "Shop"
        if self.shop_data:
            title = self.shop_data.store_name
            
        draw_text(screen, title, "HUD", 
                  x=self.rect.centerx, y=self.rect.top + 10, 
                  colour_name="SHOP_TITLE", align="midtop")
        
        #draw Slots
        super().draw(screen)
  
    def handle_click(self, pos):
        """Handles interaction. Returns a string action code if the State needs to react."""
        if not self.is_open: return False

        for slot in self.slots:
            if slot.is_click(pos) and slot.item:
                # We found the target, now pass it to logic
                return self.try_buy_item(slot.item)
        return False

    def try_buy_item(self, item:Item):
        """Validates and executes the purchase logic"""
        cost = item.data.buy_price
        # Check Money
        if self.player.money < cost:
            print(f"Cannot afford {item.name}! (Cost: {cost}, Have: {self.player.money})")
            return False

        player_item = copy.copy(item)
        player_item.count = 1 
        
        # Try and Add item
        if self.player.inventory.add_item(player_item):
            self.player.money -= cost
            print(f"Bought {player_item.name} for {cost}g.")
            return True
        print("Transaction failed (Inventory full).")
        return False