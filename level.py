import pygame, random, math
from spritesheet import SpriteSheet
from tile import Tile
from settings import BLOCK_SIZE, QUAD_SIZE
class Level:
    """ Handles level initialization by processing a node map (corner statuses)
    and generating high-resolution Marching Squares tiles. """

    def __init__(self, node_map_data: list[list[int]], all_tiles_group, 
                 player_sprite, tileset_list: list):
        
        self.node_map = node_map_data
        self.all_tiles = all_tiles_group
        self.player_sprite = player_sprite
        self.tileset = tileset_list # The list of 32x32 grass sub-tiles
        
        # The tile map dimensions are 2 less than the node map dimensions
        self.MAP_HEIGHT = len(self.node_map) - 2
        self.MAP_WIDTH = len(self.node_map[0]) - 2 

        self.generate_level()
    def generate_level(self):
        """
        Iterates over the node map to calculate the 9-node status for each 
        64x64 tile and creates the Tile object.
        """
        self.all_tiles.empty() # Clear existing tiles
        
        # Initialize the screen tile counters
        map_tile_x = 0
        map_tile_y = 0

        # We iterate over the tile coordinates (which range from 0 to MAP_SIZE-1)
        for node_y in range(0, self.MAP_HEIGHT, 2):
            map_tile_x = 0 # Reset tile X index for each new row
            for node_x in range(0, self.MAP_WIDTH, 2):
                
                # --- 1. Extract the 9-Node Status ---
                # The current tile at (tile_x, tile_y) is influenced by a 3x3 node grid 
                # starting at node (tile_x, tile_y) and ending at (tile_x + 2, tile_y + 2).
                is_water_tile = False
                nine_nodes_status = []
                for y_offset in range(3):
                    for x_offset in range(3):
                        # Accesses node_map[node_y + y_offset][node_x + x_offset]
                        node_value = self.node_map[node_y + y_offset][node_x + x_offset]
                        nine_nodes_status.append(bool(node_value))

                # --- 2. Calculate Screen Position (CORRECTED) ---
                # Use the simple map tile index (0, 1, 2, 3...) for screen position
                x = map_tile_x * BLOCK_SIZE
                y = map_tile_y * BLOCK_SIZE
                    
                # --- 3. Create the Marching Tile ---
                new_tile = Tile(
                    x, y,
                    tile_type="GRASS_A", 
                    neighbors=nine_nodes_status, # The 9 boolean nodes
                    tileset=self.tileset
                )
                
                self.all_tiles.add(new_tile)
                
                # --- 4. Place Player (using the map_tile_x/y indices) ---
                if map_tile_x == 1 and map_tile_y == 1:
                    self.player_sprite.rect.topleft = (x, y)
                    
                # --- 5. Increment Map Tile Index ---
                map_tile_x += 1 # Advance the screen position counter by 1
                
            map_tile_y += 1 # Advance the screen position counter to the next row
            
        # --- Final Dimension Calculation ---
        # Recalculate dimensions based on the tiles actually generated
        self.MAP_WIDTH = map_tile_x 
        self.MAP_HEIGHT = map_tile_y
        print(f"Level generated: {self.MAP_WIDTH}x{self.MAP_HEIGHT} tiles.")

    
    @staticmethod
    def draw_blob(node_map: list[list[int]], radius: int, passive_material: int, padding: int = 4):
        """Randomly selects a center point, calculates a noise-distorted boundary, 
        and sets nodes within that boundary to the passive_material."""
        map_size = len(node_map)

        # 1. Calculate Safe Boundaries for the Center
        min_coord = radius + padding
        max_coord = map_size - 1 - radius - padding

        # 2. Select Random Center Point (Safety check added for impossible boundaries)
        if min_coord > max_coord:
            return 
            
        center_x = random.randint(min_coord, max_coord)
        center_y = random.randint(min_coord, max_coord)
        
        # Iterate over a bounding box
        for y in range(max(0, center_y - radius - 2), min(map_size, center_y + radius + 3)):
            for x in range(max(0, center_x - radius - 2), min(map_size, center_x + radius + 3)):
                
                # 1. Calculate the distance squared from the center
                distance_sq = (x - center_x)**2 + (y - center_y)**2
                
                # 2. Calculate the Noise Value (The key to distortion)
                angle = math.atan2(y - center_y, x - center_x)
                
                # Base Distortion: A smooth wave based on the angle (3 cycles around the circle)
                distortion = math.cos(angle * 3) * 0.5 
                
                # Add subtle high-frequency randomness for texture
                noise_factor = (distortion + random.random() * 0.5) * 2
                
                # 3. Determine the effective radius for this point
                effective_radius = radius + noise_factor
                
                # 4. Check against the effective radius squared
                if distance_sq < effective_radius**2:
                    node_map[y][x] = passive_material
    @staticmethod
    def draw_pond(node_map: list[list[int]], min_radius: int = 1, max_radius: int = 2):
        """ Carves a randomly sized, organically shaped pond (Water Node = 2) 
        into the node map."""
        
        # 1. Randomly select the radius
        radius = random.randint(min_radius, max_radius)
        
        # 2. Call draw_blob with the Water Node value
        Level.draw_blob( # Need to call the static method via the class name
            node_map,
            radius=radius,
            passive_material=Level.WATER_NODE,
            padding=0
        )
    @staticmethod
    def create_node_map(map_size=32, active=1, passive=0):
        """Generates the initial node map with grass, dirt patches, and a pond."""
        # 1. Initialize the entire map grid to the active material (Grass = 1)
        node_map = [[active for _ in range(map_size)] for _ in range(map_size)]
        
        # 2. Carve out Dirt Patches (Setting nodes to 0)
        Level.draw_blob(node_map, radius=8, passive_material=passive)
        Level.draw_blob(node_map, radius=4, passive_material=passive, padding=1)
        Level.draw_blob(node_map, radius=4, passive_material=passive, padding=0)

        # 3. Add a Random Pond (WATER_NODE = 2)
        #Level.draw_pond(node_map, min_radius=6, max_radius=10)
        print("Node map created.")
        return node_map
    
    
    