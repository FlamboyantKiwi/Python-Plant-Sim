import os
from PIL import Image

def swap_dirt_columns():
    # The path to your newly sliced dirt image
    dirt_path = os.path.join("Assets", "tiles", "dirt.png")
    
    try:
        img = Image.open(dirt_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {dirt_path}. Did you run the slicing script first?")
        return
        
    TILE_SIZE = 16
    
    # The columns we want to swap (0-indexed)
    col1_idx = 8  # "Column 9"
    col2_idx = 9  # "Column 10"
    
    # 1. Calculate the bounding boxes: (left, upper, right, lower)
    # They span the entire height of the image (48px)
    col1_box = (col1_idx * TILE_SIZE, 0, (col1_idx + 1) * TILE_SIZE, img.height)
    col2_box = (col2_idx * TILE_SIZE, 0, (col2_idx + 1) * TILE_SIZE, img.height)
    
    # 2. Crop the columns out
    col1_img = img.crop(col1_box)
    col2_img = img.crop(col2_box)
    
    # 3. Paste them back in the opposite locations
    img.paste(col2_img, (col1_idx * TILE_SIZE, 0))
    img.paste(col1_img, (col2_idx * TILE_SIZE, 0))
    
    # 4. Save the modified image (overwriting the original)
    img.save(dirt_path)
    print(f"Successfully swapped columns 9 and 10 in {dirt_path}!")

if __name__ == "__main__":
    swap_dirt_columns()