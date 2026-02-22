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
                bg_colour="ButtonBG",        # Dark Grey Background
                border_colour= "ButtonBorder", # Light Grey Idle Border
                hover_colour="ButtonHover"),    # Gold Hover Border
            TextBox(
                rect=MONEY_RECT,
                text_getter=lambda: f"Money: {self.player.money}",
                config="HUD"),
        ]

    def draw(self, screen):
        for element in self.ui_elements:
            element.draw(screen)

        self.player.inventory_ui.draw(screen)

    def update(self, mouse_pos):
        for element in self.ui_elements:
            element.update(mouse_pos)
        self.player.inventory_ui.update(mouse_pos)

    def handle_click(self, pos):
        for element in self.ui_elements:
            if element.is_click(pos):
                return element.handle_click() 
            
        if self.player.handle_click(pos):
            return True
        return None
            