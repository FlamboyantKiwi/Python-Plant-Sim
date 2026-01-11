import random, math, pygame
from settings import BLOCK_SIZE, DETAIL_CHANCE
from core.asset_loader import AssetLoader
from world.tile import Tile
class Level:
    DIRT_NODE = 0
    GRASS_NODE = 1
    WATER_NODE = 2
    """ Handles level initialization by processing a node map (corner statuses)
    and generating high-resolution Marching Squares tiles. """

    def __init__(self, all_tiles_group, player_sprite, map_data: list[list[int]]|None = None):
        self.tilesets = AssetLoader.TILE_ASSETS
        self.details = AssetLoader.TILE_DETAILS
        self.all_tiles = all_tiles_group
        self.player_sprite = player_sprite
        
        if map_data:
            print("loading existing map data")
            self.node_map = map_data
        else:
            print("Generating new procdural Map")
            self.node_map = self.create_node_map(map_size=32)

        # The tile map dimensions are 2 less than the node map dimensions
        self.MAP_HEIGHT = len(self.node_map) - 2
        self.MAP_WIDTH = len(self.node_map[0]) - 2 

        self.generate_level()
    def generate_level(self):
        """ Iterates over the node map to calculate the 9-node status for each 
        64x64 tile and creates the Tile object. """
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
                nine_nodes_status = []
                same_type_count = 0
                # The primary material is based on the center node of the 3x3 grid
                center_node_material = self.node_map[node_y + 1][node_x + 1]
                for y_offset in range(3):
                    for x_offset in range(3):
                        # Accesses node_map[node_y + y_offset][node_x + x_offset]
                        node_value = self.node_map[node_y + y_offset][node_x + x_offset]
                        nine_nodes_status.append(node_value == Level.GRASS_NODE)

                        if node_value == center_node_material:
                            same_type_count += 1

                # --- 2. Calculate Screen Position (CORRECTED) ---
                # Use the simple map tile index (0, 1, 2, 3...) for screen position
                x = map_tile_x * BLOCK_SIZE
                y = map_tile_y * BLOCK_SIZE

                detail_key = None
                current_tileset = None
                
                # If dirt, use the DIRT tileset and Dirt details
                if center_node_material == Level.DIRT_NODE:
                    tile_type_key = "DIRT"
                    detail_key = "Dirt" 
                    current_tileset = self.tilesets.get("GRASS_A")

                # If grass, randomly choose between GRASS_A and GRASS_B tilesets
                elif center_node_material == Level.GRASS_NODE:
                    tile_type_key = "GRASS_A"
                    detail_key = "Grass" # Details are the same for both grass types
                    current_tileset = self.tilesets.get(tile_type_key)
                
                # Handle other types like WATER or fallback
                else: 
                    tile_type_key = "WATER" 
                    current_tileset = None
                
                # Safety check: skip if tileset is not loaded/found
                if not current_tileset:
                    print(f"Warning: Tileset '{tile_type_key}' not found.")
                    map_tile_x += 1
                    continue
                
                random_detail_image = None
                
                # Check if we have a detail key and the random chance succeeds
                if detail_key and same_type_count >= 6 and random.random() < DETAIL_CHANCE:
                    detail_list = self.details.get(detail_key)
                    
                    if detail_list:
                        # Select a random image from the list of details for this ground type
                        random_detail_image = random.choice(detail_list)

                # --- 3. Create the Marching Tile ---
                new_tile = Tile(
                    x, y,
                    tile_type=tile_type_key , 
                    neighbors=nine_nodes_status, # The 9 boolean nodes
                    tileset=current_tileset,
                    detail_image = random_detail_image)
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

    def update(self):
        """Updates all entities within the level (tiles, water animations, etc)."""
        self.all_tiles.update()
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
    @staticmethod # REMOVED (for now)
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
    
    
    