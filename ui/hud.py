from settings import WIDTH, SHOP_BUTTON, MONEY_RECT
from ui.ui_elements import Button, TextBox


class HUD:
    def __init__(self, player):
        self.player = player

        self.ui_elements = [
           Button.create_bordered_button(
                rect=SHOP_BUTTON, 
                text="SHOP", 
                function=lambda: "OPEN_SHOP",
                bg_colour=(40, 40, 40),       # Dark Grey
                border_colour=(100, 100, 100),# Light Grey Outline
                hover_colour=(255, 255, 0)),    # Yellow on Hover
            TextBox(
                rect=MONEY_RECT,
                text_getter=lambda: f"Money: {self.player.money}",
                config="HUD"),
        ]

    def draw(self, screen):
        for element in self.ui_elements:
            element.draw(screen)

        self.player.inventory.draw(screen)

    def update(self, mouse_pos):
        for element in self.ui_elements:
            element.update(mouse_pos)
        self.player.inventory.update(mouse_pos)

    def handle_click(self, pos):
        for element in self.ui_elements:
            if element.is_click(pos):
                return element.handle_click() 
            
        if self.player.inventory.handle_click(pos):
            return "INVENTORY_CLICK"
        return None
            