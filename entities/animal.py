from enum import Enum
from core.asset_loader import AssetLoader

class Animal:
    def __init__(self, x: int, y: int, type: str):
        self.pos = x, y
        self.type = type
        #self.spritesheet = AssetLoader.get_animal_image(type)
        #self.image = AssetLoader.get_animal_direction(self.spritesheet, "Idle", "Down", 0)
        
        