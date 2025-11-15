#main.py
import pygame, playerClass
from level import Level
import settings
from hud import HUD
from sys import exit
from asset_loader import AssetLoader
pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Freddy's Python Plant Sim")
clock = pygame.time.Clock()
AssetLoader()

all_sprites = pygame.sprite.Group()
all_tiles = pygame.sprite.Group()

player = playerClass.Player(settings.WIDTH//2, settings.HEIGHT//2)
all_sprites.add(player)

hud = HUD(player)

grass_tileset = AssetLoader.TILE_ASSETS.get("GRASS_A_TILES")
#dirt_tileset = AssetLoader.TILE_ASSETS.get("DIRT_TILES")

current_level = Level(
    node_map_data=Level.create_node_map(), 
    all_tiles_group=all_tiles,
    player_sprite=player,
    tileset_list=grass_tileset, 
)

playing = True
tick = 0
while playing:
    tick += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if event.type == pygame.KEYDOWN:
            player.key_down(event.key, all_tiles)
        if event.type == pygame.KEYUP:
            player.key_up(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                hud.handle_click(event.pos)
                
    screen.fill(settings.COLOURS.get("WATER", settings.DEFAULT_COLOUR))
    all_tiles.update()
    all_sprites.update(all_tiles, tick)
    hud.update(pygame.mouse.get_pos())

    all_tiles.draw(screen)
    all_sprites.draw(screen)
    hud.draw(screen)

    pygame.display.update()
    clock.tick(settings.FPS)

pygame.quit()
exit()