from PIL import Image
import os

pos = os.path.join("Assets", "tiles")

def cut_area(sheet, box, filename, pos):
    """Crops a region from the sheet and saves it to the specified position."""
    img = sheet.crop(box)
    path = os.path.join(pos, filename)
    img.save(path)
    
    # Calculate the height dynamically (lower y - upper y)
    height = box[3] - box[1]
    print(f"Saved {path} ({height}px tall)")

def slice_exterior_spritesheet():
    filename = os.path.join("Assets", "exterior.png")
    try:
        # Load the source spritesheet
        sheet = Image.open(filename).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return
    # Ensure the output directory actually exists before saving!
    os.makedirs(pos, exist_ok=True)

    # Pillow's crop uses a tuple of (left, upper, right, lower)
    # width is 160, height is 48 per region.
    
    cut_area(sheet, (0, 128, 208, 176), "cobble.png", pos)

if __name__ == "__main__":
    slice_exterior_spritesheet()