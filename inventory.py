from settings import  HIGHLIGHT_THICKNESS, HUD_FONT, SLOT_FONT, SHOP_MENU
from helper import get_image, get_colour
from item import Item
import pygame

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
                if item.stack_size > 1:
                    count_text = SLOT_FONT.render(str(item.count), True, (255, 255, 255))
                    
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
    def get_active_item(self) -> Item:
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
    def __init__(self, player, columns=4, max_size=16):
        super().__init__(max_size, columns, rect=SHOP_MENU, slot_size=70, padding=20)
        
        # Shop specific properties
        self.player = player
        self.is_open = False
        self.items = []
        self.active_slot = -1

        self.image = get_image("SHOP_MENU", (SHOP_MENU.width, SHOP_MENU.height), fallback_type="MENU")


    def toggle_open(self, hud_ref, is_open=None):
        if is_open is not None:
            self.is_open = is_open
        else:
            self.is_open = not self.is_open
        print(f"Shop is now {'OPEN' if self.is_open else 'CLOSED'}.")
    def draw(self, screen):
        if not self.is_open:
            return
        screen.blit(self.image, self.rect)
        super().draw(screen)
    def handle_click(self, pos):
        """Handles clicks on slots and the exit button."""
            
        # --- Use Inherited Method to Find Slot Index ---
        clicked_slot = self.get_slot_from_pos(pos) 
        if clicked_slot != -1 and clicked_slot < self.max_size:
            self.active_slot=clicked_slot
            if clicked_slot < len(self.items):
                item_to_buy = self.items[clicked_slot]
                self.buy_item(item_to_buy)
            return True 
        
        return False # Click was not on a valid shop item or button
