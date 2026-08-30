```mermaid
classDiagram
    UIFactory *-- TextBox : contains
    UIFactory *-- Button : contains
    UIFactory *-- InventoryUI : contains
    UIFactory *-- FlashWrapper : contains
    class Button {
        <<EXTERNAL>>
    }
    class FlashWrapper {
        <<EXTERNAL>>
    }
    class InventoryUI {
        <<EXTERNAL>>
    }
    class TextBox {
        <<EXTERNAL>>
    }
    class UIFactory {
        -_create_solid_surf()
        +bordered_slot()
        +bordered_text_button()
        +bubble_text()
        +bubble_text_button()
        +button()
        +color_swap_text_button()
        +create_grid()
        +create_vertical_stack()
        +flashing_text()
        +image_element()
        +inventory_ui()
        +inventory_with_tooltip()
        +progress_bar()
        +slot()
        +solid_element()
        +static_border_element()
        +text()
    }
```