import sqlite3

def import_old_crops():
    print("Connecting to database...")
    conn = sqlite3.connect("assets/data/gamedata.db")
    cursor = conn.cursor()

    # We translated your old CropAsset dictionary into the SQLite format!
    # Format: (id, name, grow_time, harvest_item, image_stages, is_tree, regrows, rect_x, rect_y, rect_w, rect_h)
    plants_data = [
        # 1. Green Bean (Grow: 5, Regrows: True, world_art: 0, 171, 128, 36)
        ("green_bean", "Green Bean", 5, "green_bean", 4, 0, 1, 0, 171, 128, 36),
        
        # 2. Cucumber (Grow: 5, Regrows: True, world_art: 0, 53, 128, 42)
        ("cucumber", "Cucumber", 5, "cucumber", 4, 0, 1, 0, 53, 128, 42),
        
        # 3. Red Pepper (Grow: 7, Regrows: True, world_art: 0, 95, 128, 36)
        ("red_pepper", "Red Pepper", 7, "red_pepper", 4, 0, 1, 0, 95, 128, 36),
        
        # 4. Grape (Grow: 8, Regrows: True, world_art: 0, 6, 128, 42)
        ("grape", "Grape", 8, "grape", 4, 0, 1, 0, 6, 128, 42),
        
        # 5. Pineapple (Grow: 14, Regrows: True, world_art: 0, 316, 128, 36)
        ("pineapple", "Pineapple", 14, "pineapple", 4, 0, 1, 0, 316, 128, 36)
    ]

    print("Injecting crop sprite data into the database...")
    cursor.executemany("""
        INSERT OR REPLACE INTO plants 
        (id, name, grow_time, harvest_item, image_stages, is_tree, regrows, rect_x, rect_y, rect_w, rect_h) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, plants_data)

    conn.commit()
    conn.close()
    print("Success! All your crops have been loaded with their correct sprite graphics.")


import sqlite3

def import_mushrooms():
    print("Connecting to database...")
    conn = sqlite3.connect("assets/data/gamedata.db")
    cursor = conn.cursor()

    # Format: (id, name, grow_time, harvest_item, image_stages, is_tree, regrows, rect_x, rect_y, rect_w, rect_h)
    plants_data = [
        # 1. Standard Mushroom (Grow: 3, Regrows: True, world_art: 224, 404, 64, 36)
        ("mushroom", "Mushroom", 3, "mushroom", 4, 0, 1, 224, 404, 64, 36),
        
        # 2. Chestnut Mushroom (Grow: 4, Regrows: True, world_art: 224, 368, 64, 36)
        ("chestnut_mushroom", "Chestnut Mushroom", 4, "chestnut_mushroom", 4, 0, 1, 224, 368, 64, 36)
    ]

    print("Injecting mushroom sprite data into the database...")
    cursor.executemany("""
        INSERT OR REPLACE INTO plants 
        (id, name, grow_time, harvest_item, image_stages, is_tree, regrows, rect_x, rect_y, rect_w, rect_h) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, plants_data)

    conn.commit()
    conn.close()
    print("Success! Your mushrooms have been planted in the database.")

if __name__ == "__main__":
    import_mushrooms()
    import_old_crops()