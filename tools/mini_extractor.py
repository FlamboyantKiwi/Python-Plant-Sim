import pygame

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)

    # --- 1. Load Source Images ---
    try:
        plants_img = pygame.image.load("Plants.png").convert_alpha()
        supplies_img = pygame.image.load("Supplies.png").convert_alpha()
    except FileNotFoundError as e:
        print(f"Error: Could not find source images.\nDetails: {e}")
        return

    # --- 2. Extract Sunflower World Art ---
    # Source: Plants.png | Rect(0, 396, 128, 36)
    sunflower_surf = pygame.Surface((128, 36), pygame.SRCALPHA)
    sunflower_surf.blit(plants_img, (0, 0), (0, 396, 128, 36))
    pygame.image.save(sunflower_surf, "sunflower_world_reference.png")
    print("✅ Extracted: sunflower_world_reference.png (128x36)")

    # --- 3. Extract Wheat World Art ---
    # Source: Plants.png | Rect(0, 0, 16, 16)
    wheat_surf = pygame.Surface((128, 44), pygame.SRCALPHA)
    wheat_surf.blit(plants_img, (0, 0), (0, 352, 128, 44))
    pygame.image.save(wheat_surf, "wheat_world_reference.png")
    print("✅ Extracted: wheat_world_reference.png (Directly above Sunflowers)")

    beet_surf = pygame.Surface((48, 32), pygame.SRCALPHA)
    beet_surf.blit(supplies_img, (0, 0), (224, 60, 48, 32))
    pygame.image.save(beet_surf, "beet_container_swapped.png")
    pygame.quit()

if __name__ == "__main__":
    main()