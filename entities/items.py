from abc import ABC, abstractmethod
from core.helper import get_image, load_image
from core.asset_loader import AssetLoader
from copy import copy

Default_colour = (150, 150, 150)
class Item(ABC):
    def __init__(self, name, count = 1, stack_size = 1, sell_value = 0, buy_value = 0, display_name=None, image_filename=None, image_size=48, data=None):
        self.name = name
        self.display_name = display_name if display_name else name.replace("_", " ").title()

        self.stack_size = stack_size
        self.sell_value = sell_value
        self.buy_value = buy_value
        self.data = data

        if count > self.stack_size:
            print(f"Warning! Item {self.name} initialised with a count greater than its stack size. capping at {self.stack_size}")
            self.count = self.stack_size
        else:
            self.count = count

        # Image Loading Logic
        self.image = load_image(image_filename, scale=(image_size, image_size))
    def get_stack_space(self):
        return self.stack_size - self.count
    def add_to_stack(self, amount):
        transfer_amount = min(amount, self.get_stack_space())
        self.count += transfer_amount
        return amount - transfer_amount 
    def remove_from_stack(self, amount):
        transfer_amount = min(amount, self.count)
        self.count -= transfer_amount
        return transfer_amount
    def use(self, player, target_tile, all_tiles):
        return False
    def get_name(self):
        return self.name
    def set_image(self, image):
        if image is not None:
            self.image = image
        else:
            print(f"Warning: Tool sprite not found for {self.name}. Using fallback color.")
            self.image = get_image(self.name, (32, 32), "TOOL")
    def copy_one(self):
        """Returns a new instance of this item with count 1"""
        new_item = copy.copy(self) # Shallow copy is usually enough for simple items
        new_item.count = 1
        return new_item

class Seed(Item):
    def __init__(self, name="Seed", count=1, stack_size=50, sell_value=1, buy_value=0, image_filename=None):
        name = name.title()
        super().__init__(
            name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value, 
            buy_value=buy_value,
        )
        self.set_image(AssetLoader.get_seed_image(name))
        
    def use(self, player, target_tile, all_tiles):
        if target_tile is None:
            return False # no tile to use seeds on
        pass
    def get_name(self):
        return f" {self.name} Seeds"

class Tool(Item):
    def __init__(self, name, count=1, stack_size=1, sell_value=0, buy_value=0):
        super().__init__(
            name = name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value,
            buy_value=buy_value
        )
        self.set_image(AssetLoader.get_tool_image(name))
        
    def use(self, player, target_tile, all_tiles):
        if target_tile is None:
            print("Can't find tile for interaction")
        name = self.get_name()
        match name:
            case "HOE":
                return self.hoe(player, target_tile, all_tiles)
            case "SHOVEL":
                return self.shovel(player, target_tile, all_tiles)
            case "WATERING_CAN":
                return self.water(player, target_tile, all_tiles)
            case _:
                print(f"Tool interaction for {name} is not defined.")
                return False

    def hoe(self, player, target_tile, all_tiles):
        print(f"Using {self.name}. Hoeing logic not yet implemented")
    def shovel(self, player, target_tile, all_tiles):
        print(f"Using {self.name}. Digging logic not yet implemented.")
        return False
    def water(self, player, target_tile, all_tiles):
        print(f"Using {self.name}. Watering logic not yet implemented.")
        return False
    def get_name(self):
        try:
            _, name = self.name.split("_", 1)
            return name.title()
        except ValueError:
            return self.name.title()
    

class Fruit(Item):
    def __init__(self, name, count=1, stack_size=50, sell_value=0, buy_value=0):
        super().__init__(name, count, stack_size, sell_value, buy_value)
        self.set_image(AssetLoader.get_fruit_image(name))
    def use(self, player, target_tile, all_tiles):
        print("Eating fruit")
    def get_name(self):
        try:
            _, name = self.name.split("_", 1)
            return name.title()
        except ValueError:
            return self.name.title()