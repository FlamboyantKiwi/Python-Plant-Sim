import os
from PIL import Image

def remove_cobble_duplicates():
    filepath = os.path.join("Assets", "tiles", "cobble.png")
    
    try:
        img = Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}.")
        return
        
    TILE_SIZE = 16
    
    # Create a small 16x16 transparent tile to use as an "eraser"
    empty_tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    
    # Row index 2 (Row 3), Column indexes 3, 4, 5, 6 (Cols 4-7)
    cols_to_clear = [3, 4, 5, 6]
    row_idx = 2 
    
    for col_idx in cols_to_clear:
        # Paste the transparency over the duplicate tiles
        img.paste(empty_tile, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))
        
    img.save(filepath)
    print(f"Successfully removed duplicate tiles at Row 3, Cols 4-7 in {filepath}!")

import os
from PIL import Image

def swap_cobble_columns():
    filepath = os.path.join("Assets", "tiles", "cobble.png")
    
    try:
        img = Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}.")
        return
        
    TILE_SIZE = 16
    
    # Block A: Columns 6 & 7 (Indexes 5, 6) -> starts at x=80, 32px wide
    # Block B: Columns 12 & 13 (Indexes 11, 12) -> starts at x=176, 32px wide
    
    rect_a = (5 * TILE_SIZE, 0, 7 * TILE_SIZE, img.height)
    rect_b = (11 * TILE_SIZE, 0, 13 * TILE_SIZE, img.height)
    
    # 1. Crop the blocks
    block_a = img.crop(rect_a)
    block_b = img.crop(rect_b)
    
    # 2. Swap and paste
    img.paste(block_b, (5 * TILE_SIZE, 0))
    img.paste(block_a, (11 * TILE_SIZE, 0))
    
    img.save(filepath)
    print(f"Swapped col 6/7 with col 12/13 in {filepath}!")

import os
from PIL import Image

def expand_and_move_cobble():
    filepath = os.path.join("Assets", "tiles", "cobble.png")
    
    try:
        img = Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}.")
        return
        
    TILE_SIZE = 16
    
    # 1. Create a new image that is 1 row taller (4 rows total = 64px)
    new_height = 4 * TILE_SIZE
    new_img = Image.new("RGBA", (img.width, new_height), (0, 0, 0, 0))
    
    # 2. Paste the original 3-row image onto the new canvas at the top
    new_img.paste(img, (0, 0))
    
    # 3. Define the source: Col 12/13, Row 1 (Indexes 11/12, Row 0)
    # Box: (left, upper, right, lower)
    src_x_start = 11 * TILE_SIZE
    src_x_end = 13 * TILE_SIZE
    src_y_start = 0
    src_y_end = 1 * TILE_SIZE
    
    tile_block = new_img.crop((src_x_start, src_y_start, src_x_end, src_y_end))
    
    # 4. Define the destination: Underneath Col 6/7, which is Row 4 (Index 3)
    # Col 6/7 are indexes 5 and 6
    dest_x = 5 * TILE_SIZE
    dest_y = 3 * TILE_SIZE
    
    # 5. Paste the tiles into the new row
    new_img.paste(tile_block, (dest_x, dest_y))
    
    # 6. (Optional) Clear the original Col 12/13, Row 1 if you want them moved, not copied
    # eraser = Image.new("RGBA", (32, 16), (0, 0, 0, 0))
    # new_img.paste(eraser, (src_x_start, src_y_start))
    
    new_img.save(filepath)
    print(f"Expanded {filepath} to 4 rows and moved tiles to Col 6/7, Row 4.")

import os
from PIL import Image

def remove_cobble_columns():
    filepath = os.path.join("Assets", "tiles", "cobble.png")
    
    try:
        img = Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}.")
        return
        
    TILE_SIZE = 16
    
    # Column 12/13 are indexes 11 and 12.
    # We want to keep:
    # Part 1: Everything from index 0 to 10 (Left side)
    # Part 2: Everything from index 13 onwards (Right side)
    
    # 1. Define the crop areas
    left_side = img.crop((0, 0, 11 * TILE_SIZE, img.height))
    
    # Only try to crop the right side if the image is actually wider than 13 columns
    right_side = None
    if img.width > 13 * TILE_SIZE:
        right_side = img.crop((13 * TILE_SIZE, 0, img.width, img.height))

    # 2. Calculate the new width
    new_width = left_side.width
    if right_side:
        new_width += right_side.width
        
    # 3. Create the new canvas and paste
    new_img = Image.new("RGBA", (new_width, img.height), (0, 0, 0, 0))
    new_img.paste(left_side, (0, 0))
    
    if right_side:
        new_img.paste(right_side, (left_side.width, 0))
        
    new_img.save(filepath)
    print(f"Successfully removed columns 12 and 13. New width: {new_width}px.")

if __name__ == "__main__":
    remove_cobble_columns()