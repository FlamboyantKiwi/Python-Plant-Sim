from __future__ import annotations
from .items import Item

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
        item_to_give = None
        # Create a detached copy of the item to transfer
        for item in self.items:
            if item and item.name == item_name:
                item_to_give = item.copy_one()
                item_to_give.count = amount
                break

        # Try to put it in the target's inventory
        if item_to_give and target_inventory.add_item(item_to_give):
            # If successful, remove it from our own inventory
            self.remove_item(item_name, amount)
            return True
            
        return False # Target inventory was full!
