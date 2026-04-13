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
from core.types import PlayerType
from .base import GameState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos, PlayerType

class PlayingState(GameState):
    def __init__(self, game: Game, character_type: PlayerType = PlayerType.RACOON):
        super().__init__(game)

        self.transparent = False
        self.suppress_update = True

        self.all_sprites = CameraGroup()
        self.plant_group = PlantGroup()

        self.player = Player(WIDTH // 2, HEIGHT // 2, self.all_sprites, character_type)
        self.hud = HUD(self.player)

        self.level = Level(
            plant_group=self.plant_group,
            player_sprite=self.player,
            map_data=None 
        )
     
        self.level.spawn_plant("apple", 5, 5, self.all_sprites)
        self.level.spawn_plant("onion", 6, 5, self.all_sprites)

        self.key_binds = {
            pygame.K_ESCAPE: self.game.quit,
            pygame.K_p: lambda: self.open_shop("general_store"),
            pygame.K_SPACE: lambda: self.plant_group.grow_all(0.1)
        }

    def update(self, dt:float, is_paused: bool = False):
        # Always update world animations (plants, water, etc.)
        self.level.update(dt)
        
        # 3. Handle Player Logic (Only if not paused)
        if not is_paused:
            # Gather everything the player can bump into or use
            interactables = self.level.tile_list + self.plant_group.plants
            
            # Explicitly update the player
            self.player.update(dt, interactables)

        # 4. Update the rest of the sprites (Excluding the player to avoid double-dip)
        for sprite in self.all_sprites:
            if sprite != self.player:
                # We assume other sprites only need dt for simple animations
                sprite.update(dt)
        
        # 6. Update HUD (Money/Buttons)
        mouse_pos = pygame.mouse.get_pos()
        self.hud.update(mouse_pos)
    def draw(self, screen: pygame.Surface) -> None:
        # Layer 1: The Water/Map
        screen.fill(ASSETS.colour("WATER"))
        self.level.draw(self.all_sprites.offset)
        
        # Layer 2: The Entities
        self.all_sprites.custom_draw(self.player)
        
        # Layer 3: The HUD
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
        self.game.open_shop(self.player, shop_data)
        
