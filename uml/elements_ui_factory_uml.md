```mermaid
classDiagram
    UIElement <|-- TextBox
    Sprite <|-- UIElement
    UIElement <|-- StateElement
    Button <|-- Slot
    UIElement <|-- ProgressBar
    StateElement <|-- Button
    Slot *-- Item : contains
    UIFactory ..> ShadowTextBox : creates
    UIFactory ..> UIElement : creates
    UIFactory ..> BorderSlot : creates
    UIFactory ..> ProgressBar : creates
    UIFactory ..> BorderButton : creates
    UIFactory ..> InventoryUI : creates
    UIFactory ..> Slot : creates
    UIFactory ..> TooltipWrapper : creates
    UIFactory ..> Button : creates
    UIFactory ..> FlashTextBox : creates
    UIFactory ..> TextBox : creates
    class BorderButton {
        <<EXTERNAL>>
    }
    class BorderSlot {
        <<EXTERNAL>>
    }
    class FlashTextBox {
        <<EXTERNAL>>
    }
    class InventoryUI {
        <<EXTERNAL>>
    }
    class Item {
        <<EXTERNAL>>
    }
    class ShadowTextBox {
        <<EXTERNAL>>
    }
    class Sprite {
        <<EXTERNAL>>
    }
    class TooltipWrapper {
        <<EXTERNAL>>
    }
    class TextBox {
        -_text
        +align
        +anchor_point
        +config
        +current_val
        +is_visible
        +new_text
        +text_getter
        +text_rect
        +text_surf
        -__init__(rect, text, text_getter, config, align, surface)
        -_render_text()
        +draw(screen)
        +set_text(new_text)
        +update(mouse_pos)
    }
    class UIElement {
        +image
        +is_visible
        +rect
        -__init__(rect, surface)
        +copy_image()
        +draw(screen)
        +handle_click()
        +is_click(mouse_pos)
        +update(mouse_pos)
    }
    class StateElement {
        +image
        +is_active
        +is_hovered
        -__init__(rect, base_visual)
        +update(mouse_pos)
    }
    class Slot {
        +current_count
        +index
        +info_text
        +item
        +item_rect
        +last_count
        +price
        -__init__(rect, index, base_visual)
        -_update_text()
        +draw(screen)
        +set_item(item)
        +set_price(price)
        +update(mouse_pos)
    }
    class ProgressBar {
        -_cached_size
        -_fill_surface_base
        +alignment
        +anchor_point
        +bg_element
        +dynamic_size
        +fill_element
        +is_horizontal
        +new_h
        +new_w
        +percentage
        +ratio
        +val
        +value_getter
        -__init__(rect, bg_element, fill_element, percentage, value_getter, alignment, is_horizontal)
        -_update_fill_rect()
        +draw(screen)
        +update(mouse_pos)
    }
    class Button {
        +content
        +function
        -__getattr__(attr)
        -__init__(rect, function, base_visual, content)
        +draw(screen)
        +handle_click()
        +is_click(mouse_pos)
        +update(mouse_pos)
    }
    class UIFactory {
        +base_button
        +base_inventory_ui
        +base_slot
        +base_text
        +bg_element
        +elements
        +fill_element
        +flashing_text
        +items_kwargs
        +merged_kwargs
        +rect
        +shadow_text
        +start_x
        +start_y
        +surf
        +surf_active
        +surf_hover
        +surf_normal
        +text_element
        +tooltip_box
        +total_height
        +total_items
        +v_base
        +v_normal
        -_create_solid_surf(size, colour_name)
        +bordered_slot(rect, index)
        +bordered_text_button(rect, text, function, config, bg_colour, border_colour, hover_colour, active_colour, thickness)
        +bubble_text(rect, text, text_getter, config, shadow_config, shadow_offset, align, bg_surface)
        +bubble_text_button(rect, text, function, config, shadow_config, shadow_offset, bg_colour, border_colour, hover_colour, active_colour, thickness)
        +button(rect, text, function, config)
        +color_swap_text_button(rect, text, function, config, bg_normal, bg_hover, bg_active)
        +create_grid(factory, start_pos, columns, item_size, gap, data)
        +create_vertical_stack(factory, center_pos, item_size, gap, data)
        +flashing_text(rect, text, text_getter, interval, config, align, auto_start)
        +image_element(rect, image_file)
        +inventory_ui(rect, inventory_data, columns, slot_size, padding)
        +inventory_with_tooltip(rect, inventory_data, columns, slot_size, padding, tooltip_config, tooltip_offset)
        +progress_bar(rect, percentage, value_getter, fill_colour, bg_colour, alignment, is_horizontal)
        +slot(rect, index, bg_colour, image_file)
        +solid_element(rect, colour)
        +static_border_element(rect, colour, border_colour, thickness)
        +text(rect, text, text_getter, config, align)
    }
```