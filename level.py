from tile import Ground, Water
from settings import BLOCK_SIZE, TileState

class Level:
    def __init__(self, level_data, all_tiles_group, player_sprite):
        self.level_data = level_data
        self.all_tiles = all_tiles_group
        self.player_sprite = player_sprite # Used to set the player's start position

        # Map characters to the class/state to be created
        self.tile_mapping = {
            ".": {"type": Ground, "state": TileState.UNTILLED}, # Default ground is UNTILLED
            "T": {"type": Ground, "state": TileState.TILLED},
            "P": {"type": Ground, "state": TileState.PLANTED},
            "S": None, # Future: Shop object goes here
            "W": {"type": Water}, # Future: Water or impassable terrain
        }
        
        self.parse_level()

    def parse_level(self):
        self.all_tiles.empty() # Clear any existing tiles before loading
        
        for row_index, row_string in enumerate(self.level_data):
            for col_index, char in enumerate(row_string):
                
                x = col_index * BLOCK_SIZE
                y = row_index * BLOCK_SIZE
                
                mapping = self.tile_mapping.get(char)
                
                if mapping:
                    tile_class = mapping.get("type")
                    tile_state = mapping.get("state")
                    
                    # Create the Tile object
                    new_tile = tile_class(x, y)
                    
                    # Set its specific state if applicable
                    if tile_state:
                        # NOTE: You need to implement the set_state method in your Tile class!
                        new_tile.set_state(tile_state) 
                        
                    self.all_tiles.add(new_tile)
                
                # Place the player at a starting '@' character (or similar)
                if char == "@": 
                    self.player_sprite.rect.topleft = (x, y)