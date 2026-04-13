from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

# Runtime Imports (Essential for logic/inheritance)
from entities.player import Player
from ui.hud import HUD
from world.level import Level
from settings import WIDTH, HEIGHT
from core.assets import ASSETS
from groups.camera import CameraGroup
from groups.plant_group import PlantGroup

from .base import GameState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos

class PlayingState(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.all_sprites = CameraGroup()
        self.plant_group = PlantGroup()

        self.player = Player(WIDTH // 2, HEIGHT // 2, self.all_sprites)
        self.hud = HUD(self.player)

        self.level = Level(
            plant_group=self.plant_group,
            player_sprite=self.player,
            map_data=None 
        )
     
        self.level.spawn_plant("apple", 5, 5, self.all_sprites)
        self.level.spawn_plant("onion", 6, 5, self.all_sprites)

        self.key_binds = {
            pygame.K_ESCAPE: self.quit_game,
            pygame.K_p: lambda: self.open_shop("general_store")
        }

    """def add_plant_to_world(self, plant):
        #Adds a plant to the game and links it to its tile.
        target_tile = self.level.get_tile(plant.grid_x, plant.grid_y)
        if target_tile and hasattr(target_tile, 'plant'):
            setattr(target_tile, 'plant', plant)"""

    def update(self) -> None:
        # Calculate Delta Time (dt) in seconds
        dt = self.game.clock.get_time() / 1000 
        mouse_pos = pygame.mouse.get_pos()
        
        # Update world objects
        self.level.update()
        collidables = self.level.tile_list + self.plant_group.plants
        self.all_sprites.update(dt, collidables)
        self.hud.update(mouse_pos)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.plant_group.grow_all(0.1)
                    
    def draw(self, screen: pygame.Surface) -> None:
        # Draw the game world
        screen.fill(ASSETS.colour("WATER")) 
        
        # Draw ground tiles (passing camera offset)
        self.level.draw(self.all_sprites.offset)
        
        # Draw all entities (Y-Sorted & Camera-Offset)
        self.all_sprites.custom_draw(self.player)
            
        self.hud.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        collidables = self.level.tile_list + self.plant_group.plants
        self.player.handle_event(event, collidables)
        return super().handle_event(event)

    def on_left_click(self,pos: Pos) -> None:
        action = self.hud.handle_click(pos)
        
        if action == "OPEN_SHOP":
            self.open_shop("general_store")
            return 
        elif action:
            return  
        
    def on_right_click(self, pos: Pos) -> None:
        print("Right Click detected! (Maybe cancel action?)")
        ASSETS.debug_assets()
  
    def open_shop(self, shop_id: str = "general_store") -> None:
        """ Opens the shop state with data loaded from the database. """
        from .menus import ShopState

        shop_data = ASSETS.shop(shop_id)
        self.game.push(ShopState(self.game, self.player, shop_data))
        
    def quit_game(self) -> None:
        self.game.running = False
