import pygame
from abc import ABC, abstractmethod
import tile
from settings import TileState
from helper import get_grid_pos, get_image
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

class Seed(Item):
    def __init__(self, name="Seed", count=1, stack_size=50, sell_value=1, buy_value=0, colour=None, image_size=35):
        super().__init__(
            name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value, 
            buy_value=buy_value,
            image_size=image_size,
        )
    def use(self, player, target_tile, all_tiles):
        if target_tile is None:
            return False # no tile to use seeds on
        if target_tile.state == TileState.TILLED:
            player.inventory.remove_item(self.name, 1)
            target_tile.set_state(TileState.PLANTED)
            print(f"Planted a {self.name}!")
        else:
            print(f"Cannot plant on {target_tile.state} soil. Need TILLED soil.")


class Hoe(Item):
    def __init__(self, name="Hoe", count=1, stack_size=1, sell_value=0, buy_value=0, colour=None, image_size=36):
        super().__init__(
            name = name, 
            count=count, 
            stack_size=stack_size,
            sell_value=sell_value,
            buy_value=buy_value,
            image_size=image_size,
        )
    def use(self, player, target_tile, all_tiles): 
        print("trying to use hoe")
        if target_tile:
            print("found tile")
            # Action 1: Till existing UNTILLED soil
            if hasattr(target_tile, "state"):
                if target_tile.state == TileState.UNTILLED:
                    target_tile.set_state(TileState.TILLED)
                    print("Tilled the soil!")
                    return True
                else:
                    print(f"Cannot till soil in {target_tile.state} state.")
            else:
                print("Block has no state")
        else:
            # Action 2: Place a new base tile if the space is empty
            target_x, target_y = get_grid_pos((player.rect.centerx, player.rect.bottom))
            new_tile = tile.Ground(target_x, target_y) # Tile initializes as "UNTILLED"
            all_tiles.add(new_tile)
            print("Placed new plot of UNTILLED land.")
            return True
        return False