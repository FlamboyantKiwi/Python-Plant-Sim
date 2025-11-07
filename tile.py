import pygame
from abc import ABC, abstractmethod
from settings import COLOURS, DEFAULT_COLOUR, BLOCK_SIZE, TileState
from helper import get_image
class Tile(pygame.sprite.Sprite, ABC):
    def __init__(self, x, y, image_ref):
        super().__init__()
        if hasattr(image_ref, 'name'):
            # It's an Enum member (TileState.UNTILLED), get the string name
            image_ref = image_ref.name
        self.update_visuals(image_ref)
        self.rect = self.image.get_rect(x=x, y=y) 
        self.obstructed = False
    def update_visuals(self, image_name):
        self.image = get_image(image_name, (BLOCK_SIZE, BLOCK_SIZE), self.__class__.__name__)

class Water(Tile):
    def __init__(self, x, y):
        super().__init__(x, y, "Water")
        self.obstructed = True

class Ground(Tile):
    def __init__(self, x, y):
        super().__init__(x, y, TileState.UNTILLED)
        self.state = TileState.UNTILLED
    def set_state(self, new_state):
        if new_state in TileState:
            self.state = new_state
            self.update_visuals(new_state.name)
        else:
            print(f"Warning: Unknown tile state {new_state}")
