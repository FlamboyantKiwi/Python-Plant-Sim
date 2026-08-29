import math
import random

from src.custom_types import NodeMap
from src.utils import Log


class MapGenerator:
    DIRT_NODE = 0
    GRASS_NODE = 1
    WATER_NODE = 2

    @staticmethod
    def draw_blob(node_map: NodeMap, radius: int, passive_material: int, padding: int = 4) -> None:
        """Carves a natural, noise-distorted shape (like a dirt patch) into the map grid."""
        map_size = len(node_map)
        min_coord = radius + padding
        max_coord = map_size - 1 - radius - padding

        if min_coord > max_coord:
            return
            
        center_x = random.randint(min_coord, max_coord)
        center_y = random.randint(min_coord, max_coord)
        
        for y in range(max(0, center_y - radius - 2), min(map_size, center_y + radius + 3)):
            for x in range(max(0, center_x - radius - 2), min(map_size, center_x + radius + 3)):
                distance_sq = (x - center_x)**2 + (y - center_y)**2
                angle = math.atan2(y - center_y, x - center_x)
                distortion = math.cos(angle * 3) * 0.5 
                noise_factor = (distortion + random.random() * 0.5) * 2
                effective_radius = radius + noise_factor
                
                if distance_sq < effective_radius**2:
                    node_map[y][x] = passive_material

    @staticmethod
    def generate(map_size: int = 32) -> NodeMap:
        """Creates the base 2D integer map, filling it with grass and carving out dirt patches."""
        node_map = [[MapGenerator.GRASS_NODE for _ in range(map_size)] for _ in range(map_size)]
        
        MapGenerator.draw_blob(node_map, radius=8, passive_material=MapGenerator.DIRT_NODE)
        MapGenerator.draw_blob(node_map, radius=4, passive_material=MapGenerator.DIRT_NODE, padding=1)
        MapGenerator.draw_blob(node_map, radius=4, passive_material=MapGenerator.DIRT_NODE, padding=0)
        
        Log.success("Procedural node map created.")
        return node_map