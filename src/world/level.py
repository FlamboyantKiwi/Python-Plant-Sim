from __future__ import annotations

import random
from typing import TYPE_CHECKING, cast

import pygame

# Runtime Imports
from src.config import BLOCK_SIZE, DETAIL_CHANCE
from src.core import ASSETS
from src.entities.nature.plant import Plant
from src.groups import MapTileGroup
from src.utils import Log

from .map_generator import MapGenerator
from .tiles import Tile, create_tile

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import CameraGroup, NodeMap, PlantGroup, Player

class Level:
    """Manages the active game world by translating the integer node map into physical, renderable tiles."""

    def __init__(self, plant_group: PlantGroup, player_sprite: Player, map_data: NodeMap | None = None) -> None:
        self.all_tiles = MapTileGroup()
        
        self.plant_group = plant_group
        self.player_sprite = player_sprite
        
        self.tile_grid: dict[tuple[int, int], Tile] = {}
        
        if map_data:
            Log.info("loading existing map data")
            self.node_map = map_data
        else:
            Log.info("Generating new procedural Map")
            self.node_map = MapGenerator.generate(map_size=32)

        # The tile map dimensions are 2 less than the node map dimensions
        self.MAP_HEIGHT = len(self.node_map) - 2
        self.MAP_WIDTH = len(self.node_map[0]) - 2 

        self.generate_level()

    @property
    def tile_list(self) -> list[Tile]:
        """A strictly-typed list of all active tiles in the level.
        Use this for collision and iteration instead of the raw Sprite Group."""
        return cast(list[Tile], self.all_tiles.sprites())

    def update(self, dt) -> None:
        self.all_tiles.update()

    def draw(self, camera_offset: pygame.math.Vector2) -> None:
        self.all_tiles.custom_draw(camera_offset)

    def generate_level(self) -> None:
        """Converts the integer node map into physical Pygame tile sprites using the TileFactory."""
        self.all_tiles.empty() # Clear existing tiles
        self.tile_grid.clear()
        
        # Initialize the screen tile counters
        map_tile_x = 0
        map_tile_y = 0
        for node_y in range(0, self.MAP_HEIGHT, 2):
            map_tile_x = 0
            for node_x in range(0, self.MAP_WIDTH, 2):
                
                # Determine Coordinates and Material
                x, y = map_tile_x * BLOCK_SIZE, map_tile_y * BLOCK_SIZE
                center_mat = self.node_map[node_y + 1][node_x + 1]
                
                # Process Math and Assets via Helpers
                nine_nodes, match_count = self._get_node_status(node_x, node_y, center_mat)
                tile_key, detail_img = self._get_tile_assets(center_mat, match_count)
                
                # Create Tile via Factory
                new_tile = create_tile(self, x, y, tile_key, nine_nodes, self.all_tiles, detail_img)
                self.tile_grid[(map_tile_x, map_tile_y)] = new_tile
                
                # Place Player (Spawn point)
                if map_tile_x == 1 and map_tile_y == 1:
                    self.player_sprite.rect.topleft = (x, y)
                    
                map_tile_x += 1
            map_tile_y += 1

        self.MAP_WIDTH = map_tile_x
        self.MAP_HEIGHT = map_tile_y
        Log.success(f"Level generated: {self.MAP_WIDTH}x{self.MAP_HEIGHT} tiles.")
        
    def _get_node_status(self, node_x: int, node_y: int, center_mat: int) -> tuple[list[bool], int]:
        """Checks a tile's 8 neighbors to calculate its marching squares bitmask for seamless blending."""
        nine_nodes_status = []
        same_type_count = 0
        
        for y_offset in range(3):
            for x_offset in range(3):
                node_value = self.node_map[node_y + y_offset][node_x + x_offset]
                nine_nodes_status.append(node_value == MapGenerator.GRASS_NODE)
                if node_value == center_mat:
                    same_type_count += 1
                    
        return nine_nodes_status, same_type_count
        
    def _get_tile_assets(self, center_mat: int, same_type_count: int) -> tuple[str, pygame.Surface | None]:
        """Selects the tile's base texture key and randomly applies visual details like pebbles."""
        detail_key = None
        random_detail_image = None
        
        if center_mat == MapGenerator.DIRT_NODE:
            tile_key, detail_key = "DIRT", "DETAIL_DIRT"
        elif center_mat == MapGenerator.GRASS_NODE:
            tile_key, detail_key = "GRASS_A", "DETAIL_GRASS"
        else:
            return "WATER", None
            
        # Apply random details only if the tile isn't heavily masked (same_type_count >= 6)
        if detail_key and same_type_count >= 6 and random.random() < DETAIL_CHANCE:
            detail_list = ASSETS.tiles.storage.get(detail_key)
            if detail_list:
                random_detail_image = random.choice(detail_list)
                
        return tile_key, random_detail_image 
        
    def till_map_node(self, grid_x: int, grid_y: int) -> None:
        """Updates the map data when soil is tilled and forces nearby tiles to redraw so the dirt connects seamlessly."""
        node_cx = (grid_x * 2) + 1
        node_cy = (grid_y * 2) + 1
        
        if node_cx >= len(self.node_map[0]) or node_cy >= len(self.node_map):
            return

        # Turn the center node to dirt
        self.node_map[node_cy][node_cx] = MapGenerator.DIRT_NODE
        tiles_to_refresh: set[tuple[int, int]] = {(grid_x, grid_y)}
        
        # Check Cardinals (North, South, East, West)
        # Format: (grid_offset_x, grid_offset_y, node_offset_x, node_offset_y)
        cardinals = [(0, -1, 0, -1), (0, 1, 0, 1), (-1, 0, -1, 0), (1, 0, 1, 0)]
        for dx, dy, ndx, ndy in cardinals:
            adj_tile = self.get_tile(grid_x + dx, grid_y + dy)
            if getattr(adj_tile, 'is_tilled', False):
                # If the neighbor is also tilled, turn the shared edge into dirt!
                self.node_map[node_cy + ndy][node_cx + ndx] = MapGenerator.DIRT_NODE
                tiles_to_refresh.add((grid_x + dx, grid_y + dy))

        # Check Diagonals
        diagonals = [(1, -1, 1, -1), (1, 1, 1, 1), (-1, 1, -1, 1), (-1, -1, -1, -1)]
        for dx, dy, ndx, ndy in diagonals:
            adj_tile = self.get_tile(grid_x + dx, grid_y + dy)
            # Only remove the corner node if the diagonal AND the two adjacent edges are tilled
            if getattr(adj_tile, 'is_tilled', False) and \
               getattr(self.get_tile(grid_x + dx, grid_y), 'is_tilled', False) and \
               getattr(self.get_tile(grid_x, grid_y + dy), 'is_tilled', False):
                self.node_map[node_cy + ndy][node_cx + ndx] = MapGenerator.DIRT_NODE
                tiles_to_refresh.add((grid_x + dx, grid_y + dy))

        # Tell the affected tiles to redraw
        for tx, ty in tiles_to_refresh:
            tile = self.get_tile(tx, ty)
            if tile and getattr(tile, 'tile_type_key', None) != "WATER":
                tcx, tcy = (tx * 2) + 1, (ty * 2) + 1
                new_nodes = []
                for ny in range(3):
                    for nx in range(3):
                        try:
                            val = self.node_map[tcy - 1 + ny][tcx - 1 + nx]
                            new_nodes.append(val == MapGenerator.GRASS_NODE)
                        except IndexError:
                            new_nodes.append(False) 
                
                tile.refresh_terrain(new_nodes)

    def get_tile(self, grid_x:int, grid_y:int) -> Tile|None:
        return self.tile_grid.get((grid_x, grid_y))
    
    def spawn_plant(self, plant_name: str, grid_x: int, grid_y: int, camera_group: CameraGroup) -> Plant|None:
        tile = self.get_tile(grid_x, grid_y)
        if tile: 
            tile.till()
            return tile.plant(plant_name, camera_group)
      