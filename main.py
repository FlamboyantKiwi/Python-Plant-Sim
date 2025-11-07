import pygame, playerClass
from button import Button
from level import Level
from settings import *
from hud import HUD
from sys import exit
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Freddy's Python Plant Sim")
clock = pygame.time.Clock()



all_sprites = pygame.sprite.Group()
all_tiles = pygame.sprite.Group()

player = playerClass.Player(WIDTH//2, HEIGHT//2)
all_sprites.add(player)

hud = HUD(player)

current_level = Level(
    level_data=SAMPLE_LEVEL_MAP, 
    all_tiles_group=all_tiles, 
    player_sprite=player
)

playing = True
while playing:
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
                
    #screen.fill(COLOURS.get("BG", DEFAULT_COLOUR))
    all_tiles.update()
    all_sprites.update(all_tiles)
    hud.update(pygame.mouse.get_pos())
    all_tiles.draw(screen)
    all_sprites.draw(screen)
    hud.draw(screen)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
exit()