import os
from PIL import Image

def shift_grass_tiles():
    # The path to your newly sliced grass_a image
    filepath = os.path.join("Assets", "tiles", "cobble.png")
    
    try:
        img = Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}. Did you run the slicing script first?")
        return
        
    TILE_SIZE = 16
    
    cols_to_shift = range(7, 11)
    
    for col in cols_to_shift:
        # 1. Cut out the three individual tiles for this column
        # Bounding box is (left, upper, right, lower)
        tile_row0 = img.crop((col * TILE_SIZE, 0 * TILE_SIZE, (col + 1) * TILE_SIZE, 1 * TILE_SIZE))
        tile_row2 = img.crop((col * TILE_SIZE, 2 * TILE_SIZE, (col + 1) * TILE_SIZE, 3 * TILE_SIZE))
        
        # 2. Paste them back in swapped positions
        # Row 3 (index 2) goes to Row 1 (index 0)
        img.paste(tile_row2, (col * TILE_SIZE, 0 * TILE_SIZE))
        
        # Row 1 (index 0) goes to Row 3 (index 2)
        img.paste(tile_row0, (col * TILE_SIZE, 2 * TILE_SIZE))
        
    # 3. Save the modified image (overwriting the original)
    img.save(filepath)
    print(f"Successfully shifted rows for {cols_to_shift} in {filepath}!")

if __name__ == "__main__":
    shift_grass_tiles()