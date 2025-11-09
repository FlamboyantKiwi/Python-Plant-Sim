import pygame
from settings import BLOCK_SIZE, QUAD_SIZE

MARCHING_TILES = {
    # Marching Squares Map Config
    # --- Direct Mappings (Corners Active/Grass) ---
    # 1-Sided Corners
    1: (2, 2),  # NW active
    2: (2, 0),  # NE active
    4: (0, 2),  # SW active
    8: (0, 0),  # SE active
    
    # 2-Sided Adjacent Corners (L-Shapes)
    3: (2, 1),  # NW, NE active
    5: (1, 2),  # NW, SW active
    10: (1, 0), # NE, SE active
    12: (0, 1), # SW, SE active
    
    # 4-Sided (Full Grass)
    15: (1, 1), # All active
    
    # --- Negative Mappings (Inverted/Not Grass) ---
    # These masks represent when only the specified corner is DIRT (or inactive).
    # Mask is calculated as: 15 - Corner_Bit
    
    14: (1, 4),  # NOT NW active
    13: (1, 3),  # NOT NE active
    11: (0, 4),  # NOT SW active
    7: (0, 3),   # NOT SE active
    
    # --- Diagonal Mappings (Specific two-corner pattern) ---
    9: (0, 7), # NW, SE active
    6: (0, 6), # NE, SW active
    
    # --- Default ---
    0: (0, 0),   # None active (All Dirt) - Fallback
}

# --- TILE CLASS MODIFICATION ---

class Tile(pygame.sprite.Sprite):
    BLIT_POS = [(0, 0), 
                (QUAD_SIZE, 0), 
                (0, QUAD_SIZE), 
                (QUAD_SIZE, QUAD_SIZE)]
    
    def __init__(self, position, tile_type, neighbors, tileset, sheet_width = 10):
        super().__init__()
        self.tile_type = tile_type
        self.tileset = tileset
        self.sheet_width = sheet_width
        self.position = position
        self.obstructed = False # Default unobstructed

        #Initialise 64x64 Tile Surface
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)

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
            # Calculate mask using 4 sets of 4 corners (quads)
            mask = 0
            if inputs[0]: mask += 1 # NW
            if inputs[1]: mask += 2 # NE
            if inputs[2]: mask += 4 # SW
            if inputs[3]: mask += 8 # SE
            # Get row, col coords from loopup table
            row, col = MARCHING_TILES.get(mask, (0,0))

            # Calculate linear index
            index = row * self.sheet_width + col
            # Extract + blit sub-tile onto final tile image
            sub_tile_image = self.tileset[index]
            self.image.blit(sub_tile_image, self.BLIT_POS[i])
