from .animal import Animal
from .base_entity import Entity
from .inventory_data import Inventory
from .items import FoodItem, Item, SeedItem, ToolItem, create_item
from .moving_entity import MovingEntity
from .plant import Plant
from .player import Player

## Componenets Files are Hidden:
    # They're used exclusively inside entities
    # Prevents top-level namespace clutter 
    # Avoids circular dependencies within entity classs
    
__all__ = [
    "Animal",
    "Entity",
    "FoodItem",
    "Item",
    "MovingEntity",
    "Plant",
    "Player",
    "SeedItem",
    "ToolItem",
    "create_item"
]