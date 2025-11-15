import pygame, random
from settings import QUAD_SIZE


MARCHING_TILES = {
    # Marching Squares Map Config
    # --- Direct Mappings (Corners Active/Grass) ---
    # 1-Sided Corners
    1: (2, 2),  # NW active
    2: (2, 0),  # NE active
    4: (0, 2),  # SW active
    8: (0, 0),  # SE active
    
    # 2-Sided Adjacent Corners (| Shapes)
    3: [(2, 1, 0), (2, 8, 0), (2, 9, 0)],  # NW, NE active
    5: [(1, 2, 0), (2, 8, 90), (2, 9, 90)],  # NW, SW active
    10: [(1, 0, 0), (1, 8, 90), (1, 9, 90), (0, 5, 0)], # NE, SE active
    12: [(0, 1, 0), (1, 8, 0), (1, 9, 0), (0, 5, -90)], # SW, SE active
    
    # --- Negative Mappings (Inverted/Not Grass)  (L Shape) ---
    # These masks represent when only the specified corner is DIRT (or inactive).
    # Mask is calculated as: 15 - Corner_Bit
    
    14: (1, 4),  # NOT NW active
    13: (1, 3),  # NOT NE active
    11: (0, 4),  # NOT SW active
    7: (0, 3),   # NOT SE active
    
    # --- Diagonal Mappings (Specific two-corner pattern) ( \ or / Shape)---
    9: [(0, 7, 0), (0, 8, 0), (1, 6, 0)], # NW, SE active
    6: [(0, 6, 0), (0, 9, 0), (1, 7, 0)], # NE, SW active
    
    # --- All / Nothing
    15: (1, 1), # All active (Full Grass)
    0: (2,3),   # None active (All Dirt) - Fallback
}

# --- TILE CLASS MODIFICATION ---

class Tile(pygame.sprite.Sprite):
    BLIT_POS = [(0, 0), 
                (QUAD_SIZE, 0), 
                (0, QUAD_SIZE), 
                (QUAD_SIZE, QUAD_SIZE)]
    
    def __init__(self, x, y, tile_type, neighbors, tileset, sheet_width = 10):
        from settings import BLOCK_SIZE, DIRT_TILE
        super().__init__()
        self.tile_type = tile_type
        self.sheet_width = sheet_width
        self.position = (x, y)
        self.obstructed = False # Default unobstructed

        #Initialise 64x64 Tile Surface
        self.image = DIRT_TILE.copy()
        self.rect = self.image.get_rect(topleft=self.position)
        # --- WATER OVERRIDE CHECK ---
        if not tileset:
            # If tileset is None or empty list, assign a distinct failure surface.
            self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            self.image.fill((255, 0, 255)) # Magenta failure color
            self.tileset = [] # Ensure it's not None for safety later
            print(f"ERROR: Tileset for {tile_type} is missing or empty.")
        else:
            if any(neighbors):
                self.tileset = tileset
                # create Tile's image (from 4 Sub-Tiles) using Marching Squares logic
                self.assemble_tile(neighbors)


    def assemble_tile(self, node):
        # Node List Layout:
            # node[0] node[1] node[2]
            # node[3] node[4] node[5]
            # node[6] node[7] node[8]
        quads = [ # Define the four sets of 4-bit inputs (NW, NE, SW, SE) for the quadrants
            (node[0], node[1], node[3], node[4]), # Top-Left
            (node[1], node[2], node[4], node[5]), # Top-Right
            (node[3], node[4], node[6], node[7]), # Bottom-Left
            (node[4], node[5], node[7], node[8]), # Bottom-Right
        ]

        # Iterate through the four quadrants, calculating the mask, looking up coordinates, and blitting
        for i, inputs in enumerate(quads):
            # Inputs is a tuple of 4 booleans: (NW, NE, SW, SE)
            # The bit values are 1, 2, 4, 8. We multiply the boolean (True=1, False=0) by its value.
            mask = (inputs[0] * 1) + \
                   (inputs[1] * 2) + \
                   (inputs[2] * 4) + \
                   (inputs[3] * 8)
            # Get row, col coords from loopup table
            result = MARCHING_TILES.get(mask, (2,3))

            if isinstance(result, list):
                row, col, rotation = random.choice(result)
            else:
                row, col = result
                rotation = 0

            # Calculate linear index
            index = row * self.sheet_width + col
            # Extract + blit sub-tile onto final tile image
            sub_tile_image = self.tileset[index]

            #Apply Rotation
            if rotation != 0:
                sub_tile_image = pygame.transform.rotate(sub_tile_image, rotation)

            self.image.blit(sub_tile_image, self.BLIT_POS[i])



"""class Water(Tile):
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
"""






