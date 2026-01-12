from settings import  HIGHLIGHT_THICKNESS, HUD_FONT, SLOT_FONT, SHOP_MENU
from core.helper import get_image, get_colour
from .items import Item, Seed, Fruit, Tool
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
        self.hover_border = get_colour("HOVER_COLOUR", fallback_type="HIGHLIGHT")
        self.active_border = get_colour("ACTIVE_COLOUR", fallback_type="HIGHLIGHT")
        self.active_text = get_colour("INV_TEXT", fallback_type="TEXT")

        self.grid_cols = columns
        self.grid_rows = (self.max_size + self.grid_cols - 1) //self.grid_cols # Calculate rows needed
        
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
    
    def add_item(self, new_item):
        remaining = new_item.count
        #add to existing slots
        for slot in self.items:
            if slot.name == new_item.name:
                remaining = slot.add_to_stack(remaining)
                if remaining <=0:
                    return True
        #create new slot
        while remaining > 0:
            if self.is_full():
                print(f"Inventory full! Left {remaining} {new_item.name} behind. Ouch.")
                return False # Inventory is full, cannot add more
            # Create a new slot for the remaining item
            stack_size = new_item.stack_size
            
            # Determine how many go into this new slot
            count_for_new_slot = min(remaining, stack_size)
            item_class = new_item.__class__
            # Create a new Item instance with the correct count
            new_item = item_class(
                name=new_item.name, 
                count=count_for_new_slot, 
                stack_size=stack_size,
                sell_value=new_item.sell_value, 
                buy_value=new_item.buy_value, 
            )

            self.items.append(new_item)
            remaining -= count_for_new_slot
        print(f"Added {new_item.name} to inventory")
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

    def draw(self, screen):
        #draw active item name (centered)
        name_text = HUD_FONT.render(self.get_active_item_name(), True, self.active_text)
        name_rect = name_text.get_rect(
            centerx=self.rect.centerx,
            bottom=self.rect.top - 5
        )
        screen.blit(name_text, name_rect)

        for i in range(self.max_size):
            # Calculate grid position
            col = i % self.grid_cols
            row = i // self.grid_cols
            slot_x = self.rect.x + self.padding + col * (self.slot_size + self.padding)
            slot_y = self.rect.y + self.padding + row * (self.slot_size + self.padding)
            
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            # 1. Draw the Slot Background using the image/surface (self.slot_bg_image)
            screen.blit(self.bg_image, slot_rect)

            # Draw Highlight for the Active Slot
            if i == self.active_slot:
                pygame.draw.rect(screen, self.active_border, slot_rect, HIGHLIGHT_THICKNESS)
            # Draw Highlight for Hover
            elif i == self.hover_slot:
                pygame.draw.rect(screen, self.hover_border, slot_rect, HIGHLIGHT_THICKNESS)

            # 2. Draw the item (if it exists in this slot)
            if i < len(self.items):
                item = self.items[i]
                
                # Center the item image within the slot
                item_rect = item.image.get_rect(center=slot_rect.center)
                screen.blit(item.image, item_rect)
                
                # 3. Draw the count text for stackable items
                if hasattr(item, 'stack_size') and item.stack_size > 1:
                    # Note: Added a check for 'count' just in case
                    count_val = item.count if hasattr(item, 'count') else 1
                    count_text = SLOT_FONT.render(str(count_val), True, (255, 255, 255))
                    
                    # FIX 2: count_text IS the image. It does not have an .image attribute.
                    # Position the count text in the bottom right corner of the slot
                    text_rect = count_text.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    screen.blit(count_text, text_rect)
    def update(self, pos):
        self.mouse_pos = pos
        self.hover_slot = self.get_slot_from_pos(pos)

    def get_slot_from_pos(self, pos):
        """Internal helper to convert mouse coordinates to a slot index."""
        mouse_x, mouse_y = pos
        
        # 1. Check if the mouse is even within the inventory's main rect
        if not self.rect.collidepoint(mouse_x, mouse_y):
            return -1
        
        # Calculate coordinates relative to the inventory's inner drawing area
        rel_x = mouse_x - (self.rect.x + self.padding)
        rel_y = mouse_y - (self.rect.y + self.padding)
        
        slot_size_with_padding = self.slot_size + self.padding
        
        # 2. Calculate column and row index
        col = rel_x // slot_size_with_padding
        row = rel_y // slot_size_with_padding
        
        index = row * self.grid_cols + col
        
        # 3. Final check: is the index valid and not in the padding gaps?
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
            return item.get_name()
        else:
            return ""
        

class ShopMenu(Inventory):
    def __init__(self, player, data=None, columns=4, max_size=16):
        super().__init__(max_size, columns, rect=SHOP_MENU, slot_size=70, padding=20)
        
        # Shop specific properties
        self.font = SLOT_FONT.render("Cost: $10", True, get_colour("GOLD"))
        self.player = player
        self.shop_data = data
        self.is_open = False

        self.items = []
        self.active_slot = -1

        self.image = get_image("SHOP_MENU", (SHOP_MENU.width, SHOP_MENU.height), fallback_type="MENU")
        self.populate_shop()

    def populate_shop(self):
        self.items = [] 

        CLASS_MAP = {
            "seed": Seed,
            "crop": Fruit,
            "fruit": Fruit,
            "tool": Tool,
            "misc": Item
        }
        
        # Check if shop_data exists
        if not self.shop_data or "items" not in self.shop_data:
            return

        # Iterate through the list of IDs (e.g., "tomato_seeds")
        for item_id in self.shop_data["items"]:
            
            # 1. Fetch the master data blueprint
            # If you haven't imported get_item_data, use ITEMS.get(item_id)
            item_data = ITEMS.get(item_id) 

            if not item_data: continue # Skip invalid IDs

            # 2. Look up the correct class using the category
            # default to generic Item if category isn't found
            ItemClass = CLASS_MAP.get(item_data.category, Item)

            # 3. Instantiate the class
            # Since Seed, Tool, and Fruit all take "name" (or image_key) as the first arg,
            # we can call them uniformly.
            
            # Special Handling: Tools might need underscores (e.g., "Wood Hoe" -> "Wood_Hoe")
            constructor_key = item_data.image_key
            if item_data.category == "tool":
                constructor_key = item_data.name.replace(" ", "_")

            # Create the object!
            new_item = ItemClass(constructor_key)
            
            # 4. Apply common stats from the data
            new_item.buy_value = item_data.price
            new_item.data = item_data # Link the data back to the object
            
            self.items.append(new_item)
    def toggle_open(self, hud_ref=None, is_open=None):
        if is_open is not None:
            self.is_open = is_open
        else:
            self.is_open = not self.is_open
        print(f"Shop is now {'OPEN' if self.is_open else 'CLOSED'}.")
    def draw(self, screen):
        if not self.is_open:
            return
        
        # Draw Background
        screen.blit(self.image, self.rect)

        title = "Shop"
        if self.shop_data:
            title = self.shop_data.get("type", "Shop").replace("_", " ").title()
        draw_text(screen, title, HUD_FONT, x=self.rect.centerx, y=self.rect.top+10, colour=(0,0,0))
        
        super().draw(screen)
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

            draw_text(screen, f"${item.buy_value}", SLOT_FONT, price_x, price_y, (255, 215, 0))

    def handle_click(self, pos):
        """Handles interaction. Returns a string action code if the State needs to react."""
        clicked_slot = self.get_slot_from_pos(pos) 
        if clicked_slot != -1 and clicked_slot < self.max_size:
            self.active_slot=clicked_slot
            if clicked_slot < len(self.items):
                item = self.items[clicked_slot]
                self.try_buy_item(item)
            
            return "SLOT_CLICKED"
        
        return None # Click was not on a valid shop item or button

    def try_buy_item(self, item:Item):
        """Validates and executes the purchase logic"""
        # 1. Check Gold
        if self.player.money < item.buy_value:
            print(f"Cannot afford {item.name}! (Cost: {item.buy_value}, Have: {self.player.money})")
            return False

        # 2. Check Inventory Space
        if self.player.inventory.is_full():
            print("Inventory Full!")
            return False

        # 3. Execute Transaction
        self.player.money -= item.buy_value
        new_item = copy.copy(item)
        new_item.count = 1 # Player buys 1 at a time usually
        
        self.player.inventory.add_item(new_item)
        
        print(f"Bought {item.name} for {item.buy_value}g. New Balance: {self.player.money}")
        return True