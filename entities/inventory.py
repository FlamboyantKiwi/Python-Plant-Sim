from settings import  HIGHLIGHT_THICKNESS, HUD_FONT, SLOT_FONT, SHOP_MENU, ShopData
from core.helper import get_image, get_colour
from .items import Item, ItemFactory
from Assets.asset_data import ITEMS
from core.helper import draw_text
from Assets.asset_data import ITEMS, get_item_data
import pygame, copy

class Inventory:
    def __init__(self, max_size = 4, columns = 1, rect = None, slot_size = 40, padding = 5):
        #list of Item Objects
        self.items = []
        self.max_size = max_size #total number of slots

        #Inventory Visuals
        self.slot_size = slot_size
        self.item_size = self.slot_size - 4
        self.padding = padding
        self.bg_image = get_image("slot_bg", (self.slot_size, self.slot_size), "INVENTORY_SLOT")

        #Colours 
        self.hover_border = get_colour("HOVER_COLOUR", fallback_type="HIGHLIGHT")
        self.active_border = get_colour("ACTIVE_COLOUR", fallback_type="HIGHLIGHT")
        self.active_text = get_colour("INV_TEXT", fallback_type="TEXT")

        #Grid Calculations
        self.grid_cols = columns
        self.grid_rows = (self.max_size + self.grid_cols - 1) //self.grid_cols
        
        if rect is None:
            # If no rect is provided, create a minimal default one
            default_width = columns * (self.slot_size + self.padding) + self.padding
            default_height = self.grid_rows * (self.slot_size + self.padding) + self.padding
            self.rect = pygame.Rect(0, 0, default_width, default_height)
        else:
            self.rect = rect
        
        # Add selection tracker (default to first slot)
        self.active_slot = 0    # Current selected slot index
        self.mouse_pos = (0, 0) # Stores current mouse coordinates
        self.hover_slot = -1    # Index of the slot currently under the mouse

    def is_full(self):
        return len(self.items) >= self.max_size
    
    def add_item(self, new_item:Item):
        """ Adds an item to the inventory. Handles stacking and splitting 
        large stacks into multiple slots automatically."""
        remaining = new_item.count
        #add to existing slots
        if new_item.stackable:
            for slot in self.items:
                if slot.name == new_item.name and slot.stackable:
                    remaining = slot.add_to_stack(remaining)
                    if remaining <=0:
                        return True
        #create new slot
        while remaining > 0:
            if self.is_full():
                print(f"Inventory full! Left {remaining} {new_item.name} behind. Ouch.")
                return False # Inventory is full, cannot add more
            
           # Create a NEW stack for the new slot
            new_slot_item = copy.copy(new_item)
            
            # Determine how many fit in this new slot
            if not new_item.stackable:
                # If not stackable, we can ONLY put 1 in this slot
                count_to_add = 1
            else:
                count_to_add = min(remaining, new_slot_item.stack_size)
            
            new_slot_item.count = count_to_add
            self.items.append(new_slot_item)
            
            remaining -= count_to_add
            print(f"Added new stack of {new_slot_item.name}")

        return True
    
    def remove_item(self, item_name, amount=1):
        remaining = amount
        for i in range(len(self.items) - 1, -1, -1): # iterate backwards from end of list
            item = self.items[i]
            if item.name == item_name:
                removed = item.remove_from_stack(remaining)
                remaining -= removed
                if item.count <= 0:
                    del self.items[i] # safely remove empty slot

                if remaining <= 0:
                    print(f"Successfully removed {amount} {item_name}(s).")
                    return True # Success!
        if remaining == amount:
            print(f"Couldn't find {item_name} in inventory")
        elif remaining > 0:
            print(f"Still have {remaining} {item_name} to remove!")
    def valid_slot(self, slot_id):
        """Checks if the slot_id is a valid index for the current items list."""
        if slot_id == -1: return False
        return 0 <= slot_id < len(self.items)

    def draw(self, screen):
        # Determin Display Name
        display_name = ""

        if self.valid_slot(self.hover_slot):
            display_name = self.items[self.hover_slot].name
        else:
            display_name = self.get_active_item_name()        

        name_text = HUD_FONT.render(display_name, True, self.active_text)
        name_rect = name_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        screen.blit(name_text, name_rect)

        # draw slots
        for i in range(self.max_size):
            col = i % self.grid_cols
            row = i // self.grid_cols
            slot_x = self.rect.x + self.padding + col * (self.slot_size + self.padding)
            slot_y = self.rect.y + self.padding + row * (self.slot_size + self.padding)
            
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            # Draw the Slot Background
            screen.blit(self.bg_image, slot_rect)

            # Draw Highlight for the Active Slot
            if i == self.active_slot:
                pygame.draw.rect(screen, self.active_border, slot_rect, HIGHLIGHT_THICKNESS)
            # Draw Highlight for Hover
            elif i == self.hover_slot:
                pygame.draw.rect(screen, self.hover_border, slot_rect, HIGHLIGHT_THICKNESS)

            # Draw Item Content
            if i < len(self.items):
                item = self.items[i]
                
                # Center the item image within the slot
                item_rect = item.image.get_rect(center=slot_rect.center)
                screen.blit(item.image, item_rect)
                
                # Draw stack count
                if item.stack_size > 1: 
                    count_text = SLOT_FONT.render(str(item.count), True, (255, 255, 255))
                    text_rect = count_text.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    screen.blit(count_text, text_rect)
    def update(self, pos):
        self.mouse_pos = pos
        self.hover_slot = self.get_slot_from_pos(pos)

    def get_slot_from_pos(self, pos):
        """Internal helper to convert mouse coordinates to a slot index."""
        mouse_x, mouse_y = pos
        
        # Check if the mouse is within the inventory's main rect
        if not self.rect.collidepoint(mouse_x, mouse_y): return -1
        
        # Calculate coordinates relative to the inventory's inner drawing area
        rel_x = mouse_x - (self.rect.x + self.padding)
        rel_y = mouse_y - (self.rect.y + self.padding)
        
        slot_size_with_padding = self.slot_size + self.padding
        
        # Calculate column and row index
        col = rel_x // slot_size_with_padding
        row = rel_y // slot_size_with_padding
        
        index = row * self.grid_cols + col
        
        # Final check: is the index valid and not in the padding gaps?
        if 0 <= index < self.max_size and \
           (rel_x % slot_size_with_padding) < self.slot_size and \
           (rel_y % slot_size_with_padding) < self.slot_size:
            return index
        
        return -1 # Not hovering over any slot
    
    def handle_click(self, pos):
        """Changes the active slot if a click occurs over a slot."""
        clicked_slot = self.get_slot_from_pos(pos)
        if clicked_slot != -1:
            self.active_slot = clicked_slot
            print(f"Active slot changed to: {self.active_slot + 1}")
            return True
        return False

    def set_active_slot(self, index):
        """Sets the active slot, ensuring it's within bounds."""
        if 0 <= index < self.max_size:
            self.active_slot = index
            return True
        return False
    def get_active_item(self) -> Item | None:
        """Returns the Item object currently selected, or None."""
        if 0 <= self.active_slot < len(self.items):
            return self.items[self.active_slot]
        return None
    def get_active_item_name(self):
        item = self.get_active_item()
        if item:
            return item.name
        else:
            return ""
        
class ShopMenu(Inventory):
    def __init__(self, player, data:ShopData, columns=4, max_size=16):
        super().__init__(max_size, columns, rect=SHOP_MENU, slot_size=70, padding=20)
        
        # Shop specific properties
        self.player = player
        self.shop_data = data
        self.is_open = False

        self.items:list[Item]= []
        self.active_slot = -1

        self.image = get_image("SHOP_MENU", (SHOP_MENU.width, SHOP_MENU.height), fallback_type="MENU")
        self.populate_shop()

    def populate_shop(self):
        # Reads IDs from shop_data and creates items
        self.items = [] 

        # Check if shop_data exists
        if not self.shop_data:
            return

        # Iterate through the list of item ids
        for item_id in self.shop_data.items_ids:
            
            if item_id not in ITEMS:
                print(f"Shop Warning: Item ID '{item_id}' not found.")
                continue

            # Create the item
            new_item = ItemFactory.create(item_id, count=1)
            self.items.append(new_item)
            
    def toggle_open(self, hud_ref=None, is_open=None):
        if is_open is not None:
            self.is_open = is_open
        else:
            self.is_open = not self.is_open
        print(f"Shop is now {'OPEN' if self.is_open else 'CLOSED'}.")
    def draw(self, screen):
        if not self.is_open: return
        
        # Draw Background
        screen.blit(self.image, self.rect)

        title = "Shop"
        if self.shop_data:
            title = self.shop_data.store_name
        draw_text(screen, title, HUD_FONT, x=self.rect.centerx, y=self.rect.top+10, colour=(0,0,0))
        
        #draw Slots
        super().draw(screen)
        #Drow prices
        for i, item in enumerate(self.items):
            if i >= len(self.items): break 
            
            # Calculate grid position 
            col = i % self.grid_cols
            row = i // self.grid_cols
            slot_x = self.rect.x + self.padding + col * (self.slot_size + self.padding)
            slot_y = self.rect.y + self.padding + row * (self.slot_size + self.padding)
            
            # Draw Price using your helper function
            # We use center=(x, y) logic to place it near bottom right
            price_x = slot_x + self.slot_size - 15
            price_y = slot_y + self.slot_size - 10
            
            # Optional: Draw a small black box behind the price for readability
            # (You can remove these 2 lines if you want just text)
            price_bg_rect = pygame.Rect(price_x - 15, price_y - 8, 30, 16)
            pygame.draw.rect(screen, (0,0,0), price_bg_rect, border_radius=4)

            draw_text(screen, f"${item.data.buy_price}", SLOT_FONT, price_x, price_y, (255, 215, 0))

    def handle_click(self, pos):
        """Handles interaction. Returns a string action code if the State needs to react."""
        clicked_slot = self.get_slot_from_pos(pos) 
        if self.valid_slot(clicked_slot):
            self.active_slot = clicked_slot
            item = self.items[clicked_slot]
            self.try_buy_item(item)
            return "SLOT_CLICKED"
        return None # Click was not on a valid shop item or button

    def try_buy_item(self, item:Item):
        """Validates and executes the purchase logic"""
        cost = item.data.buy_price
        # Check Money
        if self.player.money < cost:
            print(f"Cannot afford {item.name}! (Cost: {cost}, Have: {self.player.money})")
            return False

        player_item = copy.copy(item)
        player_item.count = 1 
        
        # 4. Try Add
        success = self.player.inventory.add_item(player_item)
        
        if success:
            self.player.money -= cost
            print(f"Bought {player_item.name} for {cost}g.")
            return True
        else:
            print("Transaction failed (Inventory full).")
            return False