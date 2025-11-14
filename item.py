import pygame
from abc import ABC, abstractmethod
import tile
from helper import get_grid_pos, get_image, get_tool_image, get_fruit_image, get_sprite_image

Default_colour = (150, 150, 150)
class Item(ABC):
    def __init__(self, name, count = 1, stack_size = 1, sell_value = 0, buy_value = 0, image_filename=None, image_size = 35):
        self.name = name
        self.stack_size = stack_size
        self.sell_value = sell_value
        self.buy_value = buy_value
        if count > self.stack_size:
            print(f"Warning! Item {self.name} initialised with a count greater than its stack size. capping at {self.stack_size}")
            self.count = self.stack_size
        else:
            self.count = count
        if image_filename != -1:
            self.image = get_image(image_filename, (image_size, image_size), name)

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
    @abstractmethod
    def use(self, player, target_tile, all_tiles):
        pass
    def get_name(self):
        return self.name
    def set_image(self, image):
        if image is not None:
            self.image = image
        else:
            print(f"Warning: Tool sprite not found for {self.name}. Using fallback color.")
            get_image(self.name)


class Seed(Item):
    def __init__(self, name="Seed", count=1, stack_size=50, sell_value=1, buy_value=0, image_filename=None):
        super().__init__(
            name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value, 
            buy_value=buy_value,
        )
        self.set_image(get_sprite_image(name))
    def use(self, player, target_tile, all_tiles):
        if target_tile is None:
            return False # no tile to use seeds on
        pass

class Tool(Item):
    def __init__(self, name, count=1, stack_size=1, sell_value=0, buy_value=0):
        super().__init__(
            name = name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value,
            buy_value=buy_value,
            image_filename=-1,
        )
        self.set_image(get_tool_image(name))
        
    def use(self, player, target_tile, all_tiles):
        tool_name = self.name.upper()
        match tool_name:
            case "HOE":
                return self.hoe(player, target_tile, all_tiles)
            case "SHOVEL":
                return self.shovel(player, target_tile, all_tiles)
            case "WATERING_CAN":
                return self.water(player, target_tile, all_tiles)
            case _:
                print("Tool interaction for {tool_name} is not defined.")
                return False

    def hoe(self, player, target_tile, all_tiles):
        print("trying to use hoe")
        if target_tile:
            print("found tile")
            # Action 1: Till existing UNTILLED soil
    def shovel(self, player, target_tile, all_tiles):
        print(f"Using {self.material} Shovel. Digging logic not yet implemented.")
        return False

    def water(self, player, target_tile, all_tiles):
        print(f"Using {self.material} Watering Can. Watering logic not yet implemented.")
        return False
    def get_name(self):
        _, name = self.name.split("_", 1)
        return name.title()
    

class Fruit(Item):
    def __init__(self, name, count=1, stack_size=1, sell_value=0, buy_value=0):
        super().__init__(name, count, stack_size, sell_value, buy_value, image_filename=-1)
        self.set_image(get_fruit_image(name))
    def use(self, player, target_tile, all_tiles):
        print("Eating fruit")
    def get_name(self):
        _, name = self.name.split("_", 1)
        return name.title()